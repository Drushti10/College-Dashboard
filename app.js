const express = require('express');
const path = require('path');
const session = require('express-session');
const fs = require('fs');

const app = express();
const PORT = process.env.PORT || 3000;
const DATA = path.join(__dirname, 'data');
const file = name => path.join(DATA, name);

function read(name, fallback = []) {
  try {
    if (!fs.existsSync(file(name))) return fallback;
    const content = fs.readFileSync(file(name), 'utf8');
    return JSON.parse(content);
  } catch (err) {
    console.error(`Error reading ${name}:`, err.message);
    return fallback;
  }
}

function write(name, data) {
  try {
    fs.writeFileSync(file(name), JSON.stringify(data, null, 2), 'utf8');
  } catch (err) {
    console.error(`Error writing ${name}:`, err.message);
  }
}

app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));
app.use(session({
  secret: 'mit-academy-dashboard-2026-secure-key',
  resave: false,
  saveUninitialized: false,
  cookie: { maxAge: 1000 * 60 * 60 * 4 } // 4 hours
}));

const timetable = [
  { day: 'Monday', time: '09:00 AM', subject: 'Data Structures & Algorithms', code: 'DSA', room: 'Lab 2', faculty: 'Prof. S. R. Joshi' },
  { day: 'Monday', time: '11:00 AM', subject: 'Database Management Systems', code: 'DBMS', room: 'Room 304', faculty: 'Prof. Ananya Kulkarni' },
  { day: 'Tuesday', time: '10:00 AM', subject: 'Machine Learning', code: 'ML', room: 'Lab 1', faculty: 'Dr. V. M. Deshmukh' },
  { day: 'Wednesday', time: '09:00 AM', subject: 'Design & Analysis of Algorithms', code: 'DAA', room: 'Room 202', faculty: 'Prof. R. P. Kulkarni' },
  { day: 'Thursday', time: '11:00 AM', subject: 'Computer Networks', code: 'CN', room: 'Room 105', faculty: 'Prof. A. T. Shinde' },
  { day: 'Friday', time: '10:00 AM', subject: 'Software Engineering', code: 'SE', room: 'Room 201', faculty: 'Prof. K. N. Patil' }
];

// Authentication Middleware
function auth(req, res, next) {
  if (!req.session.user) return res.redirect('/login');
  next();
}

function studentOnly(req, res, next) {
  if (!req.session.user) return res.redirect('/login');
  if (req.session.user.role !== 'student') return res.status(403).render('403', { user: req.session.user });
  next();
}

function teacherOnly(req, res, next) {
  if (!req.session.user) return res.redirect('/login');
  if (req.session.user.role !== 'teacher') return res.status(403).render('403', { user: req.session.user });
  next();
}

// Student Data Helpers
function currentStudent(req) {
  const students = read('students.json', []);
  if (!req.session.user) return students[0] || {};
  return students.find(s => s.id === req.session.user.id) ||
         students.find(s => s.rollNo === req.session.user.rollNo) ||
         students[0] || {};
}

function subjectData(studentId) {
  const marks = read('marks.json', []).filter(m => Number(m.studentId) === Number(studentId));
  const attendance = read('attendance.json', []).filter(a => Number(a.studentId) === Number(studentId));
  const defaults = [
    ['DSA', 'Data Structures & Algorithms'],
    ['DBMS', 'Database Management Systems'],
    ['ML', 'Machine Learning'],
    ['CN', 'Computer Networks'],
    ['DAA', 'Design & Analysis of Algorithms'],
    ['SE', 'Software Engineering']
  ];
  return defaults.map(([code, name]) => {
    const m = marks.find(x => x.code === code || x.subject === name);
    const a = attendance.find(x => x.code === code || x.subject === name || (code === 'DSA' && x.subject === 'DSA') || (code === 'ML' && x.subject === 'Machine Learning') || (code === 'DBMS' && x.subject === 'DBMS'));
    return {
      code,
      name,
      marks: m ? Number(m.marks) : 0,
      max: m ? Number(m.max || 100) : 100,
      attendance: a ? Number(a.percentage) : 0
    };
  });
}

function calculateAcademicHealth(studentId) {
  const student = read('students.json', []).find(s => Number(s.id) === Number(studentId)) || {};
  const subjects = subjectData(studentId);
  const assignments = read('assignments.json', []);
  
  const avgAttendance = student.attendance || 
    (subjects.length ? Math.round(subjects.reduce((sum, s) => sum + s.attendance, 0) / subjects.length) : 80);
  
  const avgMarks = subjects.length 
    ? Math.round(subjects.reduce((sum, s) => sum + s.marks, 0) / subjects.length) 
    : 75;

  const completedAssignments = assignments.filter(a => a.status === 'Completed' || a.status === 'Submitted').length;
  const assignmentRate = assignments.length ? Math.round((completedAssignments / assignments.length) * 100) : 85;

  // Consistency: penalty for high standard deviation across subjects
  const markScores = subjects.map(s => s.marks);
  const mean = avgMarks;
  const variance = markScores.length 
    ? markScores.reduce((acc, val) => acc + Math.pow(val - mean, 2), 0) / markScores.length 
    : 0;
  const stdDev = Math.sqrt(variance);
  const consistency = Math.max(50, Math.min(98, Math.round(100 - (stdDev * 1.5))));

  // Weighted Academic Health: Attendance 30%, Marks 40%, Assignments 20%, Consistency 10%
  const compositeScore = Math.round(
    (avgAttendance * 0.30) + 
    (avgMarks * 0.40) + 
    (assignmentRate * 0.20) + 
    (consistency * 0.10)
  );

  let status = 'Good';
  let badgeClass = 'status-good';
  if (compositeScore >= 80) {
    status = 'Excellent';
    badgeClass = 'status-excellent';
  } else if (compositeScore < 65) {
    status = 'Needs Attention';
    badgeClass = 'status-warning';
  }

  return {
    score: compositeScore,
    status,
    badgeClass,
    breakdown: {
      attendance: avgAttendance,
      marks: avgMarks,
      assignments: assignmentRate,
      consistency
    }
  };
}

function getPriorityTasks() {
  const assignments = read('assignments.json', []);
  const today = new Date('2026-09-09'); // Reference current academic date

  const urgent = [];
  const upcoming = [];
  const later = [];
  const completed = [];

  assignments.forEach(a => {
    if (a.status === 'Completed' || a.status === 'Submitted') {
      completed.push(a);
      return;
    }
    const dueDate = new Date(a.due);
    const diffDays = Math.ceil((dueDate - today) / (1000 * 60 * 60 * 24));
    
    if (diffDays <= 2) {
      urgent.push({ ...a, diffDays, label: diffDays <= 1 ? (diffDays === 0 ? 'Due today' : 'Due tomorrow') : `Due in ${diffDays} days` });
    } else if (diffDays <= 5) {
      upcoming.push({ ...a, diffDays, label: `Due in ${diffDays} days` });
    } else {
      later.push({ ...a, diffDays, label: `Due in ${diffDays} days` });
    }
  });

  return { urgent, upcoming, later, completed, all: assignments };
}

function getStudyPlan(studentId) {
  const plans = read('study_plans.json', {});
  if (plans[studentId]) return plans[studentId];
  if (plans['1']) return plans['1'];
  
  // Default dynamic study plan
  return [
    {
      day: 'Monday',
      slots: [
        { time: '05:00 PM – 06:15 PM', subject: 'DBMS Revision', topic: 'Indexing & Normalization', tag: 'Core Review', completed: true },
        { time: '06:30 PM – 07:45 PM', subject: 'DSA Practice', topic: 'Graph Algorithms & LeetCode', tag: 'Coding', completed: false }
      ]
    },
    {
      day: 'Tuesday',
      slots: [
        { time: '05:00 PM – 06:30 PM', subject: 'Machine Learning', topic: 'Neural Networks & Loss Functions', tag: 'Theory', completed: false },
        { time: '07:00 PM – 08:00 PM', subject: 'Assignment Work', topic: 'DAA Greedy Approaches', tag: 'Deadline', completed: false }
      ]
    },
    {
      day: 'Wednesday',
      slots: [
        { time: '05:30 PM – 07:00 PM', subject: 'Computer Networks', topic: 'Subnetting & Routing Tables', tag: 'Lab Review', completed: false }
      ]
    },
    {
      day: 'Thursday',
      slots: [
        { time: '05:00 PM – 06:30 PM', subject: 'Software Engineering', topic: 'Sprint Planning & Testing', tag: 'Project', completed: false }
      ]
    },
    {
      day: 'Friday',
      slots: [
        { time: '05:00 PM – 06:30 PM', subject: 'Targeted Review', topic: 'Weak Topics & Mock Questions', tag: 'Assessment', completed: false }
      ]
    }
  ];
}

function getSkills(studentId) {
  const skillsData = read('skills.json', {});
  return skillsData[studentId] || skillsData['1'] || [
    { name: 'Python & Data Science', category: 'Core Tech', level: 'Advanced', progress: 88, milestone: 'NumPy, Pandas & PyTorch' },
    { name: 'SQL & Database Design', category: 'Data', level: 'Proficient', progress: 82, milestone: 'Complex Queries & Indexing' },
    { name: 'Data Structures & Algorithms', category: 'Core Tech', level: 'Proficient', progress: 85, milestone: 'Trees, Graphs, DP (180+ Solved)' },
    { name: 'Machine Learning', category: 'AI / ML', level: 'Intermediate', progress: 76, milestone: 'Supervised Models & CNNs' },
    { name: 'Technical Communication', category: 'Soft Skills', level: 'Advanced', progress: 86, milestone: 'Seminars & Documentation' }
  ];
}

// Teacher Analytics & At-Risk Logic
function getAtRiskStudents() {
  const students = read('students.json', []);
  const marks = read('marks.json', []);
  const attendance = read('attendance.json', []);
  const assignments = read('assignments.json', []);

  return students.map(student => {
    const studentMarks = marks.filter(m => Number(m.studentId) === Number(student.id));
    const studentAtt = attendance.filter(a => Number(a.studentId) === Number(student.id));
    
    const avgMarks = studentMarks.length 
      ? Math.round(studentMarks.reduce((sum, m) => sum + Number(m.marks), 0) / studentMarks.length) 
      : Math.round(student.cgpa * 9.5);

    const avgAttendance = student.attendance || 
      (studentAtt.length ? Math.round(studentAtt.reduce((sum, a) => sum + Number(a.percentage), 0) / studentAtt.length) : 75);

    // Identify risk factors
    const factors = [];
    if (avgAttendance < 65) factors.push(`Critical attendance (${avgAttendance}%)`);
    else if (avgAttendance < 75) factors.push(`Low attendance (${avgAttendance}%)`);

    if (avgMarks < 55) factors.push(`Low subject marks (${avgMarks}%)`);
    else if (avgMarks < 65) factors.push(`Borderline marks (${avgMarks}%)`);

    if (student.cgpa < 6.0) factors.push(`Low CGPA (${student.cgpa.toFixed(2)})`);

    // Risk Classification
    let riskLevel = 'LOW RISK';
    let riskClass = 'risk-low';

    if (avgAttendance < 65 || avgMarks < 55 || student.cgpa < 6.0) {
      riskLevel = 'HIGH RISK';
      riskClass = 'risk-high';
    } else if (avgAttendance < 75 || avgMarks < 65 || student.cgpa < 6.8) {
      riskLevel = 'MEDIUM RISK';
      riskClass = 'risk-medium';
    }

    return {
      ...student,
      avgMarks,
      avgAttendance,
      riskLevel,
      riskClass,
      factors
    };
  });
}

function getClassAnalytics() {
  const students = read('students.json', []);
  const marks = read('marks.json', []);
  const attendance = read('attendance.json', []);
  const assignments = read('assignments.json', []);
  const atRiskList = getAtRiskStudents();

  const totalStudents = students.length;
  const avgCgpa = totalStudents 
    ? (students.reduce((sum, s) => sum + Number(s.cgpa || 0), 0) / totalStudents).toFixed(2) 
    : '0.00';

  const avgAttendance = totalStudents 
    ? Math.round(students.reduce((sum, s) => sum + Number(s.attendance || 0), 0) / totalStudents) 
    : 0;

  const totalMarksCount = marks.length;
  const classAvgMarks = totalMarksCount 
    ? Math.round(marks.reduce((sum, m) => sum + Number(m.marks || 0), 0) / totalMarksCount) 
    : 0;

  const completedAssignments = assignments.filter(a => a.status === 'Completed' || a.status === 'Submitted').length;
  const assignmentCompletionRate = assignments.length ? Math.round((completedAssignments / assignments.length) * 100) : 0;

  const passingMarks = marks.filter(m => Number(m.marks) >= 40).length;
  const passPercentage = totalMarksCount ? Math.round((passingMarks / totalMarksCount) * 100) : 100;

  // Subject performance comparison
  const subjects = ['DSA', 'DBMS', 'ML', 'CN', 'DAA', 'SE'];
  const subjectAverages = subjects.map(code => {
    const subMarks = marks.filter(m => m.code === code);
    const avg = subMarks.length ? Math.round(subMarks.reduce((sum, m) => sum + Number(m.marks), 0) / subMarks.length) : 0;
    return { code, average: avg };
  });

  // Attendance distribution (<75%, 75-85%, >85%)
  const attendanceBrackets = {
    below75: students.filter(s => Number(s.attendance) < 75).length,
    midRange: students.filter(s => Number(s.attendance) >= 75 && Number(s.attendance) <= 85).length,
    above85: students.filter(s => Number(s.attendance) > 85).length
  };

  const topStudents = [...students].sort((a, b) => b.cgpa - a.cgpa).slice(0, 4);
  const studentsNeedingAttention = atRiskList.filter(s => s.riskLevel === 'HIGH RISK' || s.riskLevel === 'MEDIUM RISK');

  return {
    totalStudents,
    avgCgpa,
    avgAttendance,
    classAvgMarks,
    assignmentCompletionRate,
    passPercentage,
    subjectAverages,
    attendanceBrackets,
    topStudents,
    studentsNeedingAttention,
    highRiskCount: atRiskList.filter(s => s.riskLevel === 'HIGH RISK').length,
    mediumRiskCount: atRiskList.filter(s => s.riskLevel === 'MEDIUM RISK').length
  };
}

// Question Paper Generator Curriculum Bank
const QUESTION_BANK = {
  'Data Structures & Algorithms': {
    'Trees': [
      { q: 'Define an AVL tree and explain the four rotation cases (LL, RR, LR, RL) with diagrams.', marks: 10, type: 'Long Answer' },
      { q: 'Construct a Binary Search Tree for elements [45, 23, 76, 12, 34, 67, 89, 29]. Show deletion of node 45.', marks: 8, type: 'Problem Solving' },
      { q: 'Compare Red-Black Tree vs AVL Tree in terms of insertion overhead and search performance.', marks: 6, type: 'Analytical' },
      { q: 'Write an algorithm for preorder and inorder traversal reconstruction of a binary tree.', marks: 8, type: 'Algorithm' },
      { q: 'What is the maximum number of nodes in a binary tree of height h? Prove by induction.', marks: 4, type: 'Short Answer' },
      { q: 'Explain Huffman coding algorithm and compute the optimal prefix code tree for given frequencies.', marks: 10, type: 'Long Answer' },
      { q: 'Differentiate between B-Tree and B+ Tree with their search complexity.', marks: 6, type: 'Conceptual' },
      { q: 'Explain Breadth-First Search (BFS) on graphs and analyze its time and space complexity.', marks: 6, type: 'Algorithm' }
    ],
    'Graphs': [
      { q: 'Explain Dijkstra\'s single-source shortest path algorithm. Trace on a directed weighted graph with 6 vertices.', marks: 10, type: 'Algorithm' },
      { q: 'Differentiate between Prim\'s and Kruskal\'s Minimum Spanning Tree algorithms with time complexities.', marks: 8, type: 'Analytical' },
      { q: 'What is topological sorting? State the conditions under which it exists for a directed graph.', marks: 5, type: 'Short Answer' },
      { q: 'Explain Floyd-Warshall algorithm for all-pairs shortest paths with dynamic programming formulation.', marks: 10, type: 'Algorithm' }
    ],
    'Sorting & Searching': [
      { q: 'Analyze the best, average, and worst-case time complexities of QuickSort with recurrence relations.', marks: 8, type: 'Analytical' },
      { q: 'Implement MergeSort on an array and explain why it is preferred for linked lists.', marks: 8, type: 'Algorithm' },
      { q: 'Explain Heap Sort with max-heapify and build-heap procedures.', marks: 8, type: 'Algorithm' }
    ]
  },
  'Database Management Systems': {
    'Normalization': [
      { q: 'Explain 1NF, 2NF, 3NF, and BCNF with concrete relation schemas and functional dependencies.', marks: 10, type: 'Theory' },
      { q: 'Given relation R(A, B, C, D, E) with FDs {A->BC, CD->E, B->D, E->A}. Find candidate keys and highest normal form.', marks: 10, type: 'Problem Solving' },
      { q: 'What is lossless-join decomposition and dependency preservation? State the formal tests.', marks: 6, type: 'Conceptual' },
      { q: 'Why is BCNF strictly stronger than 3NF? Provide an example relation in 3NF but not in BCNF.', marks: 6, type: 'Analytical' }
    ],
    'SQL & Transactions': [
      { q: 'Explain ACID properties of transactions and how the DBMS guarantees each property.', marks: 8, type: 'Theory' },
      { q: 'Explain Two-Phase Locking (2PL) protocol and prove that Strict 2PL ensures conflict serializability.', marks: 10, type: 'Analytical' },
      { q: 'Write complex SQL queries using window functions, GROUP BY HAVING, and correlated subqueries.', marks: 8, type: 'Problem Solving' },
      { q: 'Explain B+ Tree index architecture and how multi-level indexing accelerates range queries.', marks: 8, type: 'Conceptual' }
    ]
  },
  'Machine Learning': {
    'Supervised Learning': [
      { q: 'Derive the gradient descent weight update rule for Logistic Regression with binary cross-entropy loss.', marks: 10, type: 'Mathematical' },
      { q: 'Explain the bias-variance tradeoff and how regularization (L1 Lasso vs L2 Ridge) mitigates overfitting.', marks: 8, type: 'Analytical' },
      { q: 'Formulate Support Vector Machine (SVM) maximal margin hyperplane optimization problem with dual formulation.', marks: 10, type: 'Mathematical' },
      { q: 'Differentiate between Random Forest and Gradient Boosted Decision Trees (GBDT).', marks: 6, type: 'Conceptual' }
    ],
    'Neural Networks': [
      { q: 'Derive the backpropagation algorithm for a multi-layer perceptron using the chain rule of calculus.', marks: 10, type: 'Mathematical' },
      { q: 'Explain Convolutional Neural Network (CNN) architecture: convolution, stride, padding, and pooling layers.', marks: 10, type: 'Architecture' },
      { q: 'Compare activation functions: Sigmoid, Tanh, ReLU, and Leaky ReLU with their vanishing gradient behavior.', marks: 6, type: 'Analytical' },
      { q: 'What is Batch Normalization and Dropout? How do they stabilize deep neural network training?', marks: 8, type: 'Conceptual' }
    ]
  },
  'Computer Networks': {
    'Transport Layer': [
      { q: 'Explain TCP 3-way handshake and 4-way connection teardown with state transition diagrams.', marks: 10, type: 'Protocol' },
      { q: 'Analyze TCP Congestion Control algorithms: Slow Start, Congestion Avoidance, Fast Retransmit, and Fast Recovery.', marks: 10, type: 'Protocol' },
      { q: 'Compare TCP vs UDP headers and explain why real-time streaming prefers UDP.', marks: 6, type: 'Conceptual' }
    ],
    'Network Layer': [
      { q: 'Given IPv4 block 192.168.10.0/24, design 4 subnets with required host capacities using CIDR VLSM.', marks: 10, type: 'Numerical' },
      { q: 'Explain Distance Vector Routing vs Link State Routing algorithms with count-to-infinity mitigation.', marks: 10, type: 'Analytical' },
      { q: 'Explain ARP protocol operation and format of ARP request and reply frames.', marks: 6, type: 'Protocol' }
    ]
  }
};

function generateQuestionPaper({ subject, topic, difficulty, numQuestions, maxMarks }) {
  const count = Number(numQuestions) || 5;
  const marks = Number(maxMarks) || 50;
  
  // Find questions from question bank
  let pool = [];
  const subjectEntry = QUESTION_BANK[subject];
  if (subjectEntry) {
    if (topic && subjectEntry[topic]) {
      pool = [...subjectEntry[topic]];
    } else {
      // aggregate all topics in subject
      Object.values(subjectEntry).forEach(qList => pool.push(...qList));
    }
  }

  // Fallback if subject or topic not matched
  if (!pool.length) {
    pool = [
      { q: `Explain the fundamental architecture and principles of ${topic || subject}.`, marks: 10, type: 'Core Theory' },
      { q: `Analyze the time and space computational efficiency in ${topic || subject} implementations.`, marks: 8, type: 'Analysis' },
      { q: `Design an end-to-end algorithmic workflow for a real-world application in ${topic || subject}.`, marks: 10, type: 'System Design' },
      { q: `Compare traditional methodologies versus modern industry paradigms in ${subject}.`, marks: 8, type: 'Analytical' },
      { q: `Describe error mitigation, edge-case handling, and performance optimizations in ${topic || subject}.`, marks: 8, type: 'Problem Solving' },
      { q: `Provide a detailed case study illustrating practical deployment of ${topic || subject}.`, marks: 6, type: 'Case Study' }
    ];
  }

  // Select questions according to requested count
  const selected = [];
  for (let i = 0; i < count; i++) {
    const item = pool[i % pool.length];
    selected.push({
      qNum: i + 1,
      text: item.q,
      marks: Math.max(2, Math.round(marks / count)),
      type: item.type || 'Descriptive',
      difficulty: difficulty || 'Medium'
    });
  }

  // Organize into sections
  const sectionA = selected.slice(0, Math.ceil(count * 0.4));
  const sectionB = selected.slice(Math.ceil(count * 0.4));

  return {
    institution: 'MIT ACADEMY OF ENGINEERING, PUNE',
    subHeader: 'An Autonomous Institute Affiliated to Savitribai Phule Pune University',
    department: 'Department of Computer Engineering',
    examTitle: 'Continuous Internal Assessment Examination (CIA - 2026)',
    subject,
    topic: topic || 'All Core Modules',
    difficulty: difficulty || 'Medium',
    duration: count <= 5 ? '1 Hour' : count <= 10 ? '2 Hours' : '3 Hours',
    maxMarks: marks,
    dateGenerated: new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' }),
    instructions: [
      'All questions are compulsory.',
      'Figures to the right indicate full marks.',
      'Assume suitable data wherever necessary and state it clearly.',
      'Draw neat sketches / circuit diagrams / flowcharts wherever required.'
    ],
    sections: [
      { title: 'Section A: Conceptual Understanding & Analytical Questions', questions: sectionA },
      { title: 'Section B: Comprehensive Problem Solving & Design Questions', questions: sectionB }
    ]
  };
}

function commonData(req) {
  return {
    user: req.session.user,
    students: read('students.json', []),
    marks: read('marks.json', []),
    attendance: read('attendance.json', []),
    assignments: read('assignments.json', []),
    notices: read('notices.json', []),
    interventions: read('interventions.json', []),
    timetable
  };
}

// Routes
app.get('/', (req, res) => {
  if (!req.session.user) return res.redirect('/login');
  res.redirect(req.session.user.role === 'teacher' ? '/teacher' : '/dashboard');
});

// Login & Auth
app.get('/login', (req, res) => {
  if (req.session.user) {
    return res.redirect(req.session.user.role === 'teacher' ? '/teacher' : '/dashboard');
  }
  res.render('login', { error: null });
});

app.post('/login', (req, res) => {
  const { email, password } = req.body;
  const users = read('users.json', []);
  const user = users.find(u => u.email === (email || '').trim().toLowerCase() && u.password === (password || '').trim());
  
  if (!user) {
    return res.render('login', { error: 'Invalid institutional email or password. Please verify credentials.' });
  }
  
  req.session.user = user;
  req.session.justLoggedIn = true;
  res.redirect(user.role === 'teacher' ? '/teacher' : '/dashboard');
});

app.get('/logout', (req, res) => {
  req.session.destroy(() => res.redirect('/login'));
});

// ==================== STUDENT ROUTES ====================
app.get('/dashboard', studentOnly, (req, res) => {
  const student = currentStudent(req);
  const data = commonData(req);
  const subjects = subjectData(student.id);
  const myMarks = data.marks.filter(m => Number(m.studentId) === Number(student.id));
  const myAttendance = data.attendance.filter(a => Number(a.studentId) === Number(student.id));
  const showPopup = Boolean(req.session.justLoggedIn);
  req.session.justLoggedIn = false;

  const academicHealth = calculateAcademicHealth(student.id);
  const priorityTasks = getPriorityTasks();
  const studyPlan = getStudyPlan(student.id);
  const skills = getSkills(student.id);

  res.render('student/dashboard', {
    ...data,
    student,
    subjects,
    myMarks,
    myAttendance,
    academicHealth,
    priorityTasks,
    studyPlan,
    skills,
    showPopup,
    active: 'dashboard'
  });
});

app.get('/profile', studentOnly, (req, res) => {
  const student = currentStudent(req);
  const academicHealth = calculateAcademicHealth(student.id);
  const skills = getSkills(student.id);
  res.render('student/profile', {
    ...commonData(req),
    student,
    academicHealth,
    skills,
    active: 'profile'
  });
});

app.get('/attendance', studentOnly, (req, res) => {
  const student = currentStudent(req);
  const subjects = subjectData(student.id);
  const academicHealth = calculateAcademicHealth(student.id);
  res.render('student/attendance', {
    ...commonData(req),
    student,
    subjects,
    academicHealth,
    active: 'attendance'
  });
});

app.get('/marks', studentOnly, (req, res) => {
  const student = currentStudent(req);
  const subjects = subjectData(student.id);
  const academicHealth = calculateAcademicHealth(student.id);
  res.render('student/marks', {
    ...commonData(req),
    student,
    subjects,
    academicHealth,
    active: 'marks'
  });
});

app.get('/assignments', studentOnly, (req, res) => {
  const student = currentStudent(req);
  const priorityTasks = getPriorityTasks();
  res.render('student/assignments', {
    ...commonData(req),
    student,
    priorityTasks,
    active: 'assignments',
    message: req.query.message
  });
});

app.post('/assignments/:id/submit', studentOnly, (req, res) => {
  const assignments = read('assignments.json', []);
  const item = assignments.find(a => String(a.id) === String(req.params.id));
  if (item && item.status !== 'Completed') {
    item.status = 'Submitted';
    write('assignments.json', assignments);
  }
  res.redirect('/assignments?message=Assignment%20submitted%20successfully%20for%20review');
});

app.get('/timetable', studentOnly, (req, res) => {
  const student = currentStudent(req);
  res.render('student/timetable', {
    ...commonData(req),
    student,
    active: 'timetable'
  });
});

app.get('/notices', studentOnly, (req, res) => {
  const student = currentStudent(req);
  res.render('student/notices', {
    ...commonData(req),
    student,
    active: 'notices'
  });
});

// ==================== TEACHER ROUTES ====================
app.get('/teacher', teacherOnly, (req, res) => {
  const data = commonData(req);
  const analytics = getClassAnalytics();
  const atRiskList = getAtRiskStudents();
  res.render('teacher/dashboard', {
    ...data,
    analytics,
    atRiskList,
    averageCgpa: analytics.avgCgpa,
    active: 'dashboard',
    message: req.query.message
  });
});

// Teacher Analytics
app.get('/teacher/analytics', teacherOnly, (req, res) => {
  const data = commonData(req);
  const analytics = getClassAnalytics();
  const atRiskList = getAtRiskStudents();
  res.render('teacher/analytics', {
    ...data,
    analytics,
    atRiskList,
    active: 'analytics'
  });
});

// Teacher At-Risk Students
app.get('/teacher/at-risk', teacherOnly, (req, res) => {
  const data = commonData(req);
  const atRiskList = getAtRiskStudents();
  res.render('teacher/at-risk', {
    ...data,
    atRiskList,
    active: 'at-risk'
  });
});

// Teacher Student 360 Profile
app.get('/teacher/students/:id/profile', teacherOnly, (req, res) => {
  const data = commonData(req);
  const studentId = Number(req.params.id);
  const student = data.students.find(s => Number(s.id) === studentId);
  if (!student) return res.redirect('/teacher/students');
  
  const subjects = subjectData(student.id);
  const academicHealth = calculateAcademicHealth(student.id);
  const studentInterventions = data.interventions.filter(i => Number(i.studentId) === studentId);
  const atRiskInfo = getAtRiskStudents().find(s => Number(s.id) === studentId);

  res.render('teacher/student-profile', {
    ...data,
    student,
    subjects,
    academicHealth,
    studentInterventions,
    atRiskInfo,
    active: 'students'
  });
});

// Teacher Question Paper Generator
app.get('/teacher/question-generator', teacherOnly, (req, res) => {
  res.render('teacher/question-generator', {
    ...commonData(req),
    paper: null,
    active: 'question-generator'
  });
});

app.post('/teacher/question-generator', teacherOnly, (req, res) => {
  const { subject, topic, difficulty, numQuestions, maxMarks } = req.body;
  const paper = generateQuestionPaper({ subject, topic, difficulty, numQuestions, maxMarks });
  res.render('teacher/question-generator', {
    ...commonData(req),
    paper,
    active: 'question-generator'
  });
});

// Teacher Interventions CRUD
app.get('/teacher/interventions', teacherOnly, (req, res) => {
  res.render('teacher/interventions', {
    ...commonData(req),
    active: 'interventions',
    message: req.query.message
  });
});

app.post('/teacher/interventions', teacherOnly, (req, res) => {
  const interventions = read('interventions.json', []);
  const students = read('students.json', []);
  const studentId = Number(req.body.studentId);
  const student = students.find(s => Number(s.id) === studentId);

  const nextId = interventions.length ? Math.max(...interventions.map(i => Number(i.id))) + 1 : 1;
  const newIntervention = {
    id: nextId,
    studentId,
    studentName: student ? student.name : 'Unknown Student',
    rollNo: student ? student.rollNo : 'N/A',
    issue: (req.body.issue || '').trim(),
    action: (req.body.action || '').trim(),
    followUpDate: req.body.followUpDate || '',
    status: req.body.status || 'Pending',
    createdDate: new Date().toISOString().split('T')[0],
    facultyName: req.session.user.name || 'Faculty Member'
  };

  interventions.unshift(newIntervention);
  write('interventions.json', interventions);
  res.redirect('/teacher/interventions?message=Intervention%20note%20recorded%20successfully');
});

app.post('/teacher/interventions/:id/status', teacherOnly, (req, res) => {
  const interventions = read('interventions.json', []);
  const item = interventions.find(i => Number(i.id) === Number(req.params.id));
  if (item) {
    item.status = item.status === 'Completed' ? 'Pending' : 'Completed';
    write('interventions.json', interventions);
  }
  res.redirect('/teacher/interventions?message=Status%20updated%20successfully');
});

app.post('/teacher/interventions/:id/delete', teacherOnly, (req, res) => {
  const id = Number(req.params.id);
  write('interventions.json', read('interventions.json', []).filter(i => Number(i.id) !== id));
  res.redirect('/teacher/interventions?message=Intervention%20deleted%20successfully');
});

// Students CRUD
app.get('/teacher/students', teacherOnly, (req, res) => {
  res.render('teacher/students', {
    ...commonData(req),
    active: 'students',
    message: req.query.message
  });
});

app.post('/teacher/students', teacherOnly, (req, res) => {
  const students = read('students.json', []);
  const nextId = students.length ? Math.max(...students.map(s => Number(s.id))) + 1 : 1;
  const name = (req.body.name || '').trim();
  const rollNo = (req.body.rollNo || '').trim();
  if (name && rollNo) {
    students.push({
      id: nextId,
      name,
      rollNo,
      course: (req.body.course || 'B.E. Computer Science (Data Science)').trim(),
      year: req.body.year || '2nd Year',
      semester: req.body.semester || 'IV',
      email: req.body.email || `${rollNo.toLowerCase()}@college.com`,
      phone: req.body.phone || '+91 90000 00000',
      cgpa: Number(req.body.cgpa) || 0,
      attendance: Number(req.body.attendance) || 0,
      avatar: name.split(/\s+/).map(x => x[0]).join('').slice(0, 2).toUpperCase()
    });
    write('students.json', students);
  }
  res.redirect('/teacher/students?message=Student%20created%20successfully');
});

app.post('/teacher/students/:id/update', teacherOnly, (req, res) => {
  const students = read('students.json', []);
  const s = students.find(x => Number(x.id) === Number(req.params.id));
  if (s) {
    Object.assign(s, {
      name: req.body.name?.trim() || s.name,
      rollNo: req.body.rollNo?.trim() || s.rollNo,
      course: req.body.course?.trim() || s.course,
      year: req.body.year || s.year,
      semester: req.body.semester || s.semester,
      email: req.body.email || s.email,
      phone: req.body.phone || s.phone,
      cgpa: Number(req.body.cgpa ?? s.cgpa),
      attendance: Number(req.body.attendance ?? s.attendance)
    });
    write('students.json', students);
  }
  res.redirect('/teacher/students?message=Student%20updated%20successfully');
});

app.post('/teacher/students/:id/delete', teacherOnly, (req, res) => {
  const id = Number(req.params.id);
  write('students.json', read('students.json', []).filter(s => Number(s.id) !== id));
  write('marks.json', read('marks.json', []).filter(m => Number(m.studentId) !== id));
  write('attendance.json', read('attendance.json', []).filter(a => Number(a.studentId) !== id));
  write('interventions.json', read('interventions.json', []).filter(i => Number(i.studentId) !== id));
  res.redirect('/teacher/students?message=Student%20deleted%20successfully');
});

// Marks CRUD
app.get('/teacher/marks', teacherOnly, (req, res) => {
  res.render('teacher/marks', {
    ...commonData(req),
    active: 'marks',
    message: req.query.message
  });
});

app.post('/teacher/marks', teacherOnly, (req, res) => {
  const marks = read('marks.json', []);
  const nextId = marks.length ? Math.max(...marks.map(m => Number(m.id))) + 1 : 1;
  marks.push({
    id: nextId,
    studentId: Number(req.body.studentId),
    subject: req.body.subject,
    code: req.body.code,
    marks: Number(req.body.marks),
    max: Number(req.body.max || 100)
  });
  write('marks.json', marks);
  res.redirect('/teacher/marks?message=Marks%20created%20successfully');
});

app.post('/teacher/marks/:id/update', teacherOnly, (req, res) => {
  const marks = read('marks.json', []);
  const m = marks.find(x => Number(x.id) === Number(req.params.id));
  if (m) {
    Object.assign(m, {
      studentId: Number(req.body.studentId),
      subject: req.body.subject,
      code: req.body.code,
      marks: Number(req.body.marks),
      max: Number(req.body.max || 100)
    });
    write('marks.json', marks);
  }
  res.redirect('/teacher/marks?message=Marks%20updated%20successfully');
});

app.post('/teacher/marks/:id/delete', teacherOnly, (req, res) => {
  write('marks.json', read('marks.json', []).filter(m => Number(m.id) !== Number(req.params.id)));
  res.redirect('/teacher/marks?message=Marks%20deleted%20successfully');
});

// Attendance CRUD
app.get('/teacher/attendance', teacherOnly, (req, res) => {
  res.render('teacher/attendance', {
    ...commonData(req),
    active: 'attendance',
    message: req.query.message
  });
});

app.post('/teacher/attendance', teacherOnly, (req, res) => {
  const attendance = read('attendance.json', []);
  const nextId = attendance.length ? Math.max(...attendance.map(x => Number(x.id))) + 1 : 1;
  attendance.push({
    id: nextId,
    studentId: Number(req.body.studentId),
    subject: req.body.subject,
    percentage: Number(req.body.percentage)
  });
  write('attendance.json', attendance);
  res.redirect('/teacher/attendance?message=Attendance%20recorded%20successfully');
});

app.post('/teacher/attendance/:id/update', teacherOnly, (req, res) => {
  const attendance = read('attendance.json', []);
  const a = attendance.find(x => Number(x.id) === Number(req.params.id));
  if (a) {
    Object.assign(a, {
      studentId: Number(req.body.studentId),
      subject: req.body.subject,
      percentage: Number(req.body.percentage)
    });
    write('attendance.json', attendance);
  }
  res.redirect('/teacher/attendance?message=Attendance%20updated%20successfully');
});

app.post('/teacher/attendance/:id/delete', teacherOnly, (req, res) => {
  write('attendance.json', read('attendance.json', []).filter(a => Number(a.id) !== Number(req.params.id)));
  res.redirect('/teacher/attendance?message=Attendance%20deleted%20successfully');
});

// Assignment CRUD
app.get('/teacher/assignments', teacherOnly, (req, res) => {
  res.render('teacher/assignments', {
    ...commonData(req),
    active: 'assignments',
    message: req.query.message
  });
});

app.post('/teacher/assignments', teacherOnly, (req, res) => {
  const assignments = read('assignments.json', []);
  const nextId = assignments.length ? Math.max(...assignments.map(x => Number(x.id))) + 1 : 1;
  assignments.push({
    id: nextId,
    title: req.body.title,
    subject: req.body.subject,
    due: req.body.due,
    status: req.body.status || 'Pending',
    description: req.body.description || ''
  });
  write('assignments.json', assignments);
  res.redirect('/teacher/assignments?message=Assignment%20created%20successfully');
});

app.post('/teacher/assignments/:id/update', teacherOnly, (req, res) => {
  const assignments = read('assignments.json', []);
  const a = assignments.find(x => Number(x.id) === Number(req.params.id));
  if (a) {
    Object.assign(a, {
      title: req.body.title,
      subject: req.body.subject,
      due: req.body.due,
      status: req.body.status,
      description: req.body.description || a.description
    });
    write('assignments.json', assignments);
  }
  res.redirect('/teacher/assignments?message=Assignment%20updated%20successfully');
});

app.post('/teacher/assignments/:id/delete', teacherOnly, (req, res) => {
  write('assignments.json', read('assignments.json', []).filter(a => Number(a.id) !== Number(req.params.id)));
  res.redirect('/teacher/assignments?message=Assignment%20deleted%20successfully');
});

// Notices CRUD
app.get('/teacher/notices', teacherOnly, (req, res) => {
  res.render('teacher/notices', {
    ...commonData(req),
    active: 'notices',
    message: req.query.message
  });
});

app.post('/teacher/notices', teacherOnly, (req, res) => {
  const notices = read('notices.json', []);
  const nextId = notices.length ? Math.max(...notices.map(x => Number(x.id))) + 1 : 1;
  const type = req.body.type || 'General';
  let icon = '📢';
  if (type === 'Academic') icon = '📝';
  else if (type === 'Event') icon = '💡';
  else if (type === 'Placement') icon = '💼';
  else if (type === 'Library') icon = '📚';

  notices.unshift({
    id: nextId,
    title: (req.body.title || '').trim(),
    message: (req.body.message || '').trim(),
    date: req.body.date || new Date().toISOString().split('T')[0],
    type,
    priority: req.body.priority || 'Normal',
    icon,
    author: req.body.author || req.session.user.name || 'Faculty Office'
  });
  write('notices.json', notices);
  res.redirect('/teacher/notices?message=Notice%20published%20successfully');
});

app.post('/teacher/notices/:id/update', teacherOnly, (req, res) => {
  const notices = read('notices.json', []);
  const n = notices.find(x => Number(x.id) === Number(req.params.id));
  if (n) {
    Object.assign(n, {
      title: req.body.title,
      message: req.body.message,
      date: req.body.date,
      type: req.body.type,
      priority: req.body.priority || n.priority
    });
    write('notices.json', notices);
  }
  res.redirect('/teacher/notices?message=Notice%20updated%20successfully');
});

app.post('/teacher/notices/:id/delete', teacherOnly, (req, res) => {
  write('notices.json', read('notices.json', []).filter(n => Number(n.id) !== Number(req.params.id)));
  res.redirect('/teacher/notices?message=Notice%20deleted%20successfully');
});

// Error handling
app.use((req, res) => res.status(404).render('404', { user: req.session ? req.session.user : null }));

app.listen(PORT, () => console.log(`MIT Academy Smart Academic Portal running at http://localhost:${PORT}`));

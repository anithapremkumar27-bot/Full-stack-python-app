// TodoSphere Frontend SPA State and Interaction Engine

// --- STATE MANAGEMENT ---
let appState = {
    categories: [],
    activeCategoryId: null, // null means "All Categories"
    tasks: [],
    searchQuery: '',
    priorityFilter: 'All'
};

// Chart.js global instances
let statusChartInstance = null;
let priorityChartInstance = null;

// API Endpoints Base
const API_BASE = '/api';

// --- DOM ELEMENTS ---
const categoryListEl = document.getElementById('category-list');
const activeCategoryNameEl = document.getElementById('active-category-name');
const activeCategoryDescEl = document.getElementById('active-category-desc');
const btnCreateTaskMain = document.getElementById('btn-create-task-main');
const taskSearchInput = document.getElementById('task-search-input');
const priorityFilterSelect = document.getElementById('priority-filter');

// Modals & Forms
const categoryModal = document.getElementById('category-modal');
const taskModal = document.getElementById('task-modal');
const categoryForm = document.getElementById('category-form');
const taskForm = document.getElementById('task-form');

// Counters
const countTotalEl = document.getElementById('count-total');
const countTodoEl = document.getElementById('count-todo');
const countProgressEl = document.getElementById('count-progress');
const countDoneEl = document.getElementById('count-done');

// Kanban column bodies
const colTodo = document.getElementById('col-todo');
const colProgress = document.getElementById('col-progress');
const colCompleted = document.getElementById('col-completed');

// --- INITIALIZATION ---
document.addEventListener('DOMContentLoaded', () => {
    setupEventListeners();
    fetchCategories().then(() => {
        fetchTasks();
    });
});

// --- EVENT LISTENERS SETUP ---
function setupEventListeners() {
    // Category modal triggers
    document.getElementById('btn-add-category').addEventListener('click', () => openModal(categoryModal));
    document.getElementById('btn-close-category-modal').addEventListener('click', () => closeModal(categoryModal));
    document.getElementById('btn-cancel-category').addEventListener('click', () => closeModal(categoryModal));
    
    // Category Form Submit
    categoryForm.addEventListener('submit', handleCategorySubmit);

    // Color picker value label sync
    const colorInput = document.getElementById('category-color-input');
    const colorLabel = document.querySelector('.color-value-label');
    if (colorInput && colorLabel) {
        colorInput.addEventListener('input', (e) => {
            colorLabel.textContent = e.target.value.toUpperCase();
        });
    }

    // Task modal triggers
    btnCreateTaskMain.addEventListener('click', () => {
        if (appState.categories.length === 0) {
            alert('Please create at least one category first.');
            return;
        }
        resetTaskForm();
        document.getElementById('task-modal-title').textContent = 'Add New Task';
        openModal(taskModal);
    });
    document.getElementById('btn-close-task-modal').addEventListener('click', () => closeModal(taskModal));
    document.getElementById('btn-cancel-task').addEventListener('click', () => closeModal(taskModal));

    // Task Form Submit
    taskForm.addEventListener('submit', handleTaskSubmit);

    // Search and Filters
    taskSearchInput.addEventListener('input', (e) => {
        appState.searchQuery = e.target.value.toLowerCase();
        renderBoard();
        renderCharts();
    });

    priorityFilterSelect.addEventListener('change', (e) => {
        appState.priorityFilter = e.target.value;
        renderBoard();
        renderCharts();
    });

    // Handle dragover visual feedback on column bodies
    [colTodo, colProgress, colCompleted].forEach(col => {
        col.addEventListener('dragenter', (e) => {
            e.preventDefault();
            col.classList.add('drag-over');
        });
        col.addEventListener('dragleave', (e) => {
            col.classList.remove('drag-over');
        });
    });
}

// --- MODAL CONTROLS ---
function openModal(modalEl) {
    modalEl.classList.add('open');
}

function closeModal(modalEl) {
    modalEl.classList.remove('open');
}

function resetTaskForm() {
    taskForm.reset();
    document.getElementById('task-id-input').value = '';
    document.getElementById('task-date-input').value = '';
    
    // Default task category selection logic:
    // If we have an active category, select it in the dropdown; otherwise select the first option
    const categorySelect = document.getElementById('task-category-input');
    if (categorySelect) {
        if (appState.activeCategoryId) {
            categorySelect.value = appState.activeCategoryId;
        } else if (categorySelect.options.length > 0) {
            categorySelect.selectedIndex = 0;
        }
    }
}

function resetCategoryForm() {
    categoryForm.reset();
    document.getElementById('category-color-input').value = '#8B5CF6';
    document.querySelector('.color-value-label').textContent = '#8B5CF6';
}

// --- API COMMUNICATIONS ---

// Categories
async function fetchCategories() {
    try {
        const res = await fetch(`${API_BASE}/categories`);
        if (!res.ok) throw new Error('Failed to fetch categories');
        appState.categories = await res.json();
        
        renderCategories();
        populateTaskCategoryDropdown();
    } catch (err) {
        console.error(err);
        categoryListEl.innerHTML = `<div class="error-text" style="color:#ef4444;padding:10px;">Error loading categories.</div>`;
    }
}

async function handleCategorySubmit(e) {
    e.preventDefault();
    const name = document.getElementById('category-name-input').value.trim();
    const color = document.getElementById('category-color-input').value;

    try {
        const res = await fetch(`${API_BASE}/categories`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, color })
        });
        
        if (!res.ok) {
            const data = await res.json();
            alert(data.detail || 'Could not create category');
            return;
        }

        const newCat = await res.json();
        closeModal(categoryModal);
        resetCategoryForm();
        
        // Re-fetch list
        await fetchCategories();
        selectCategory(newCat.id);
    } catch (err) {
        console.error(err);
    }
}

async function deleteCategory(categoryId, event) {
    event.stopPropagation(); // Avoid selecting category on delete click
    if (!confirm('Are you sure you want to delete this category? All associated tasks will be lost.')) return;

    try {
        const res = await fetch(`${API_BASE}/categories/${categoryId}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Delete failed');
        
        if (appState.activeCategoryId === categoryId) {
            appState.activeCategoryId = null;
        }
        
        await fetchCategories();
        fetchTasks();
    } catch (err) {
        console.error(err);
    }
}

function selectCategory(categoryId) {
    appState.activeCategoryId = categoryId;
    
    // Update active class in sidebar
    const items = categoryListEl.querySelectorAll('.category-item');
    items.forEach(item => {
        const itemCatId = item.dataset.id === 'null' ? null : parseInt(item.dataset.id);
        if (itemCatId === categoryId) {
            item.classList.add('active');
        } else {
            item.classList.remove('active');
        }
    });

    // Update details panel heading
    if (categoryId === null) {
        activeCategoryNameEl.textContent = 'All Categories';
        activeCategoryDescEl.textContent = 'Viewing all tasks across all categories.';
    } else {
        const cat = appState.categories.find(c => c.id === categoryId);
        if (cat) {
            activeCategoryNameEl.textContent = cat.name;
            activeCategoryDescEl.textContent = `Viewing tasks assigned to the "${cat.name}" category.`;
        }
    }
    
    // Re-render dashboard counters, charts, and kanban board
    renderBoard();
    updateDashboardCounters();
    renderCharts();
}

// Tasks
async function fetchTasks() {
    try {
        const res = await fetch(`${API_BASE}/tasks`);
        if (!res.ok) throw new Error('Failed to fetch tasks');
        appState.tasks = await res.json();
        
        renderBoard();
        updateDashboardCounters();
        renderCharts();
    } catch (err) {
        console.error(err);
    }
}

async function handleTaskSubmit(e) {
    e.preventDefault();
    const taskId = document.getElementById('task-id-input').value;
    const title = document.getElementById('task-title-input').value.trim();
    const description = document.getElementById('task-desc-input').value.trim();
    const status = document.getElementById('task-status-input').value;
    const priority = document.getElementById('task-priority-input').value;
    const category_id = parseInt(document.getElementById('task-category-input').value);
    const due_date = document.getElementById('task-date-input').value || null;

    const taskPayload = { title, description, status, priority, due_date, category_id };

    try {
        let res;
        if (taskId) {
            // Update task details
            res = await fetch(`${API_BASE}/tasks/${taskId}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(taskPayload)
            });
        } else {
            // Create new task
            res = await fetch(`${API_BASE}/tasks`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(taskPayload)
            });
        }

        if (!res.ok) {
            const data = await res.json();
            throw new Error(data.detail || 'Failed to save task');
        }
        
        closeModal(taskModal);
        fetchTasks();
    } catch (err) {
        console.error(err);
        alert(err.message);
    }
}

async function startEditTask(taskId, event) {
    event.stopPropagation();
    const task = appState.tasks.find(t => t.id === taskId);
    if (!task) return;

    resetTaskForm();
    document.getElementById('task-modal-title').textContent = 'Edit Task';
    document.getElementById('task-id-input').value = task.id;
    document.getElementById('task-title-input').value = task.title;
    document.getElementById('task-desc-input').value = task.description || '';
    document.getElementById('task-status-input').value = task.status;
    document.getElementById('task-priority-input').value = task.priority;
    document.getElementById('task-category-input').value = task.category_id;
    
    if (task.due_date) {
        document.getElementById('task-date-input').value = task.due_date;
    }

    openModal(taskModal);
}

async function deleteTask(taskId, event) {
    event.stopPropagation();
    if (!confirm('Are you sure you want to delete this task?')) return;

    try {
        const res = await fetch(`${API_BASE}/tasks/${taskId}`, { method: 'DELETE' });
        if (!res.ok) throw new Error('Delete task failed');
        fetchTasks();
    } catch (err) {
        console.error(err);
    }
}

// --- RENDERING WORKSPACE ---

function renderCategories() {
    categoryListEl.innerHTML = '';
    
    // Add default "All Categories" list item
    const allItem = document.createElement('div');
    allItem.className = `category-item ${appState.activeCategoryId === null ? 'active' : ''}`;
    allItem.dataset.id = 'null';
    allItem.onclick = () => selectCategory(null);
    
    // Calculate total count
    const totalCount = appState.tasks ? appState.tasks.length : 0;
    
    allItem.innerHTML = `
        <div class="category-meta">
            <span class="category-color-dot" style="background-color: var(--primary);"></span>
            <span class="category-title">All Categories</span>
        </div>
        <span class="category-count" id="count-all-badge">${totalCount}</span>
    `;
    categoryListEl.appendChild(allItem);

    // List individual categories
    appState.categories.forEach(c => {
        const isActive = c.id === appState.activeCategoryId;
        
        // Count tasks in this category
        const count = appState.tasks ? appState.tasks.filter(t => t.category_id === c.id).length : 0;
        
        const categoryItem = document.createElement('div');
        categoryItem.className = `category-item ${isActive ? 'active' : ''}`;
        categoryItem.dataset.id = c.id;
        categoryItem.onclick = () => selectCategory(c.id);
        
        categoryItem.innerHTML = `
            <div class="category-meta">
                <span class="category-color-dot" style="background-color: ${c.color};"></span>
                <span class="category-title" title="${c.name}">${c.name}</span>
            </div>
            <div style="display:flex;align-items:center;gap:6px;">
                <span class="category-count">${count}</span>
                <button class="category-item-delete" onclick="deleteCategory(${c.id}, event)" title="Delete Category">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
            </div>
        `;
        categoryListEl.appendChild(categoryItem);
    });
    
    // Keep All Categories count badge updated
    const countAllEl = document.getElementById('count-all-badge');
    if (countAllEl) {
        countAllEl.textContent = appState.tasks ? appState.tasks.length : 0;
    }
}

function populateTaskCategoryDropdown() {
    const dropdown = document.getElementById('task-category-input');
    if (!dropdown) return;
    
    dropdown.innerHTML = '';
    appState.categories.forEach(c => {
        const opt = document.createElement('option');
        opt.value = c.id;
        opt.textContent = c.name;
        dropdown.appendChild(opt);
    });
}

function renderBoard() {
    // Clear columns
    colTodo.innerHTML = '';
    colProgress.innerHTML = '';
    colCompleted.innerHTML = '';

    // Filter tasks based on Category, Search Query, and Priority Filters
    const filteredTasks = appState.tasks.filter(task => {
        const matchesCategory = appState.activeCategoryId === null || task.category_id === appState.activeCategoryId;
        const matchesSearch = task.title.toLowerCase().includes(appState.searchQuery) || 
                              (task.description && task.description.toLowerCase().includes(appState.searchQuery));
        const matchesPriority = appState.priorityFilter === 'All' || task.priority === appState.priorityFilter;
        return matchesCategory && matchesSearch && matchesPriority;
    });

    const statusCounts = {
        'To Do': 0,
        'In Progress': 0,
        'Completed': 0
    };

    filteredTasks.forEach(task => {
        statusCounts[task.status]++;
        
        const card = createTaskCard(task);
        
        switch (task.status) {
            case 'To Do':
                colTodo.appendChild(card);
                break;
            case 'In Progress':
                colProgress.appendChild(card);
                break;
            case 'Completed':
                colCompleted.appendChild(card);
                break;
        }
    });

    // Update Column Badge Counts
    document.getElementById('badge-todo').textContent = statusCounts['To Do'];
    document.getElementById('badge-progress').textContent = statusCounts['In Progress'];
    document.getElementById('badge-completed').textContent = statusCounts['Completed'];

    // Render Empty Placeholders inside columns if zero tasks
    Object.keys(statusCounts).forEach(status => {
        if (statusCounts[status] === 0) {
            const bodyEl = getColumnBodyEl(status);
            bodyEl.innerHTML = `<div class="empty-state">No tasks here</div>`;
        }
    });
}

function getColumnBodyEl(status) {
    switch (status) {
        case 'To Do': return colTodo;
        case 'In Progress': return colProgress;
        case 'Completed': return colCompleted;
    }
}

function createTaskCard(task) {
    const card = document.createElement('div');
    card.className = 'task-card';
    card.draggable = true;
    card.dataset.id = task.id;
    
    // Wire drag & drop
    card.ondragstart = (e) => dragStart(e);
    card.ondragend = (e) => dragEnd(e);

    const desc = task.description ? `<p>${task.description}</p>` : `<p class="text-muted"><i>No description.</i></p>`;
    
    // Priority badge style
    const priorityClass = `badge-${task.priority.toLowerCase()}`;
    
    // Category tag rendering
    let categoryBadgeHtml = '';
    if (task.category) {
        categoryBadgeHtml = `
            <span class="card-category-badge" style="background-color: ${task.category.color};" title="${task.category.name}">
                ${task.category.name}
            </span>
        `;
    }

    // Due date formatting and overdue check
    let dateHtml = '';
    if (task.due_date) {
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        
        // Handle timezone difference properly
        const dueDate = new Date(task.due_date + 'T00:00:00');
        
        const isOverdue = dueDate < today && task.status !== 'Completed';
        const formattedDate = dueDate.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
        
        dateHtml = `
            <div class="card-date ${isOverdue ? 'overdue' : ''}">
                <i class="fa-regular fa-calendar"></i>
                <span>${formattedDate}${isOverdue ? ' (Overdue)' : ''}</span>
            </div>
        `;
    }

    card.innerHTML = `
        <div class="card-top">
            <span class="badge-priority ${priorityClass}">${task.priority}</span>
            <div class="card-actions">
                <button class="btn-card-action edit" onclick="startEditTask(${task.id}, event)" title="Edit Task">
                    <i class="fa-solid fa-pen-to-square"></i>
                </button>
                <button class="btn-card-action delete" onclick="deleteTask(${task.id}, event)" title="Delete Task">
                    <i class="fa-solid fa-trash-can"></i>
                </button>
            </div>
        </div>
        <h5>${task.title}</h5>
        ${desc}
        <div class="card-footer">
            ${categoryBadgeHtml}
            ${dateHtml || '<div style="flex:1;"></div>'}
        </div>
    `;

    return card;
}

function updateDashboardCounters() {
    // If activeCategoryId is set, counts are for that category. Otherwise global.
    const activeTasks = appState.tasks.filter(t => appState.activeCategoryId === null || t.category_id === appState.activeCategoryId);
    
    const total = activeTasks.length;
    const todo = activeTasks.filter(t => t.status === 'To Do').length;
    const progress = activeTasks.filter(t => t.status === 'In Progress').length;
    const done = activeTasks.filter(t => t.status === 'Completed').length;

    countTotalEl.textContent = total;
    countTodoEl.textContent = todo;
    countProgressEl.textContent = progress;
    countDoneEl.textContent = done;

    // Trigger categories sidebar re-rendering (updates counts next to tags)
    renderCategories();
}

// --- DRAG AND DROP HANDLERS ---

function dragStart(e) {
    e.dataTransfer.setData('text/plain', e.target.dataset.id);
    e.target.classList.add('dragging');
}

function dragEnd(e) {
    e.target.classList.remove('dragging');
    // Remove drag-over styling from columns
    [colTodo, colProgress, colCompleted].forEach(col => {
        col.classList.remove('drag-over');
    });
}

// Allowed drops
window.allowDrop = function(e) {
    e.preventDefault();
}

window.dropTask = async function(e) {
    e.preventDefault();
    
    // Find closest column container to get the new status
    const columnBody = e.currentTarget;
    columnBody.classList.remove('drag-over');
    
    const targetStatus = columnBody.parentElement.dataset.status;
    const taskId = e.dataTransfer.getData('text/plain');
    
    if (!taskId || !targetStatus) return;

    try {
        const res = await fetch(`${API_BASE}/tasks/${taskId}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: targetStatus })
        });
        
        if (!res.ok) throw new Error('Failed to update status');
        
        // Re-load state
        fetchTasks();
    } catch (err) {
        console.error(err);
    }
}

// Attach helpers to global window for HTML drag/drop callbacks
window.dragStart = dragStart;
window.dragEnd = dragEnd;
window.startEditTask = startEditTask;
window.deleteTask = deleteTask;
window.deleteCategory = deleteCategory;

// --- CHART.JS CONFIGURATION & UPDATES ---

function renderCharts() {
    // Filter chart data by Category, Search, and Priority filter as well (making charts reactive!)
    const activeTasks = appState.tasks.filter(task => {
        const matchesCategory = appState.activeCategoryId === null || task.category_id === appState.activeCategoryId;
        const matchesSearch = task.title.toLowerCase().includes(appState.searchQuery) || 
                              (task.description && task.description.toLowerCase().includes(appState.searchQuery));
        const matchesPriority = appState.priorityFilter === 'All' || task.priority === appState.priorityFilter;
        return matchesCategory && matchesSearch && matchesPriority;
    });

    const statuses = ['To Do', 'In Progress', 'Completed'];
    const statusCounts = statuses.map(s => activeTasks.filter(t => t.status === s).length);

    const priorities = ['Low', 'Medium', 'High'];
    const priorityCounts = priorities.map(p => activeTasks.filter(t => t.priority === p).length);

    // 1. Status Chart (Doughnut)
    const canvasStatus = document.getElementById('statusChart');
    if (!canvasStatus) return;
    
    const ctxStatus = canvasStatus.getContext('2d');
    if (statusChartInstance) {
        statusChartInstance.destroy();
    }
    
    statusChartInstance = new Chart(ctxStatus, {
        type: 'doughnut',
        data: {
            labels: statuses,
            datasets: [{
                data: statusCounts,
                backgroundColor: [
                    '#3b82f6', // blue
                    '#f59e0b', // amber
                    '#10b981'  // emerald
                ],
                borderWidth: 0,
                hoverOffset: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        color: '#a1a1aa',
                        padding: 15,
                        font: { family: 'Inter', size: 11 }
                    }
                }
            },
            cutout: '75%'
        }
    });

    // 2. Priority Chart (Bar)
    const canvasPriority = document.getElementById('priorityChart');
    if (!canvasPriority) return;
    
    const ctxPriority = canvasPriority.getContext('2d');
    if (priorityChartInstance) {
        priorityChartInstance.destroy();
    }

    priorityChartInstance = new Chart(ctxPriority, {
        type: 'bar',
        data: {
            labels: priorities,
            datasets: [{
                label: 'Tasks',
                data: priorityCounts,
                backgroundColor: [
                    '#10b981', // green
                    '#f59e0b', // amber
                    '#ef4444'  // red
                ],
                borderRadius: 6,
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        color: '#a1a1aa',
                        stepSize: 1,
                        font: { family: 'Inter', size: 10 }
                    },
                    grid: {
                        color: 'rgba(255, 255, 255, 0.05)'
                    }
                },
                x: {
                    ticks: {
                        color: '#a1a1aa',
                        font: { family: 'Inter', size: 11 }
                    },
                    grid: {
                        display: false
                    }
                }
            },
            plugins: {
                legend: {
                    display: false
                }
            }
        }
    });
}

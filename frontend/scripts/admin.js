// admin.js - Admin portal logic for FixIt Tech Solutions

document.addEventListener('DOMContentLoaded', () => {
    // Dashboard stats
    async function loadDashboardStats() {
        const statsDiv = document.getElementById('dashboard-stats');
        statsDiv.innerHTML = '<div>Loading...</div>';
        try {
            const resp = await fetch('http://localhost:8080/admin/dashboard/stats');
            const stats = await resp.json();
            statsDiv.innerHTML = `
                <div class="dashboard-card"><h3>Total Bookings</h3><div class="stat">${stats.total_bookings}</div></div>
                <div class="dashboard-card"><h3>Pending</h3><div class="stat">${stats.pending}</div></div>
                <div class="dashboard-card"><h3>Today</h3><div class="stat">${stats.today}</div></div>
                <div class="dashboard-card"><h3>Confirmed</h3><div class="stat">${stats.confirmed}</div></div>
                <div class="dashboard-card"><h3>Completed</h3><div class="stat">${stats.completed}</div></div>
                <div class="dashboard-card"><h3>Cancelled</h3><div class="stat">${stats.cancelled}</div></div>
            `;
            // Optionally, update chart here in the future
        } catch (err) {
            statsDiv.innerHTML = '<div style="color:red">Failed to load stats</div>';
        }
    }

    // Device/Issue stats
    async function loadDeviceIssueStats() {
        const resp = await fetch('http://localhost:8080/admin/dashboard/device-issue-stats');
        const stats = await resp.json();
        // Device chart
        const deviceLabels = stats.device_counts.map(d => d.device);
        const deviceData = stats.device_counts.map(d => d.count);
        const deviceCtx = document.getElementById('device-chart').getContext('2d');
        new Chart(deviceCtx, {
            type: 'bar',
            data: {
                labels: deviceLabels,
                datasets: [{
                    label: 'Repairs by Device',
                    data: deviceData,
                    backgroundColor: '#2e7dff',
                }]
            },
            options: {responsive:true, plugins:{legend:{display:false}}}
        });
        // Issue chart
        const issueLabels = stats.issue_counts.map(i => i.issue);
        const issueData = stats.issue_counts.map(i => i.count);
        const issueCtx = document.getElementById('issue-chart').getContext('2d');
        new Chart(issueCtx, {
            type: 'bar',
            data: {
                labels: issueLabels,
                datasets: [{
                    label: 'Repairs by Issue',
                    data: issueData,
                    backgroundColor: '#00c6ae',
                }]
            },
            options: {responsive:true, plugins:{legend:{display:false}}}
        });
    }

    // Quick actions
    document.getElementById('refresh-dashboard').addEventListener('click', loadDashboardStats);
    document.getElementById('go-to-bookings').addEventListener('click', () => {
        document.getElementById('bookings').scrollIntoView({ behavior: 'smooth' });
    });

    // Bookings table
    async function loadBookings() {
        const tbody = document.getElementById('bookings-table-body');
        tbody.innerHTML = '<tr><td colspan="9">Loading...</td></tr>';
        const status = document.getElementById('filter-status').value;
        const from = document.getElementById('filter-from-date').value;
        const to = document.getElementById('filter-to-date').value;
        let url = 'http://localhost:8080/admin/bookings?';
        if (status) url += `status=${status}&`;
        if (from) url += `from_date=${from}&`;
        if (to) url += `to_date=${to}&`;
        try {
            const resp = await fetch(url);
            const bookings = await resp.json();
            if (!Array.isArray(bookings) || bookings.length === 0) {
                tbody.innerHTML = '<tr><td colspan="9">No bookings found.</td></tr>';
                return;
            }
            tbody.innerHTML = '';
            bookings.forEach(b => {
                tbody.innerHTML += `
                    <tr>
                        <td>${b.id}</td>
                        <td>${b.name}</td>
                        <td>${b.email}</td>
                        <td>${b.phone}</td>
                        <td>${b.device}</td>
                        <td>${b.issue}</td>
                        <td>${b.date ? new Date(b.date).toLocaleString() : ''}</td>
                        <td>
                            <select data-id="${b.id}" class="status-select">
                                <option value="pending" ${b.status==='pending'?'selected':''}>Pending</option>
                                <option value="confirmed" ${b.status==='confirmed'?'selected':''}>Confirmed</option>
                                <option value="completed" ${b.status==='completed'?'selected':''}>Completed</option>
                                <option value="cancelled" ${b.status==='cancelled'?'selected':''}>Cancelled</option>
                            </select>
                        </td>
                        <td>
                            <button class="delete-btn" data-id="${b.id}">Delete</button>
                        </td>
                    </tr>
                `;
            });
        } catch (err) {
            tbody.innerHTML = '<tr><td colspan="9" style="color:red">Failed to load bookings</td></tr>';
        }
    }

    // Filter events
    document.getElementById('filter-apply').addEventListener('click', loadBookings);

    // Status update and delete actions (event delegation)
    document.getElementById('bookings-table-body').addEventListener('change', async e => {
        if (e.target.classList.contains('status-select')) {
            const id = e.target.getAttribute('data-id');
            const status = e.target.value;
            await fetch(`http://localhost:8080/admin/bookings/${id}`, {
                method: 'PATCH',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ status })
            });
            loadDashboardStats();
        }
    });
    document.getElementById('bookings-table-body').addEventListener('click', async e => {
        if (e.target.classList.contains('delete-btn')) {
            const id = e.target.getAttribute('data-id');
            if (confirm('Delete this booking?')) {
                await fetch(`http://localhost:8080/admin/bookings/${id}`, { method: 'DELETE' });
                loadBookings();
                loadDashboardStats();
            }
        }
    });

    // Initial load
    loadDashboardStats();
    loadBookings();
    loadDeviceIssueStats();
});

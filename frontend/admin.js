const API_URL = 'PASTE_YOUR_API_URL_HERE'; // From SAM outputs

async function registerEmployee() {
    const id = document.getElementById('reg-id').value;
    const fileInput = document.getElementById('reg-file');
    const file = fileInput.files[0];

    if (!id || !file) {
        alert("Please provide Employee ID and Photo");
        return;
    }

    try {
        // 1. Get Presigned URL
        const urlRes = await fetch(`${API_URL}upload-url?type=registration&employee_id=${id}`);
        const { url } = await urlRes.json();

        // 2. Upload to S3
        await fetch(url, {
            method: 'PUT',
            body: file,
            headers: { 'Content-Type': 'image/jpeg' }
        });

        alert("Employee Registered Successfully!");
        document.getElementById('reg-id').value = '';
        fileInput.value = '';
        loadAttendance();

    } catch (err) {
        console.error("Registration error:", err);
        alert("Registration failed.");
    }
}

async function loadAttendance() {
    try {
        const res = await fetch(`${API_URL}reports`);
        const data = await res.json();
        const tbody = document.getElementById('attendance-body');
        tbody.innerHTML = '';

        data.sort((a, b) => b.PK.localeCompare(a.PK)).forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td>${row.PK.replace('EMP#', '')}</td>
                <td>${row.SK.replace('DATE#', '')}</td>
                <td>${row.clock_in ? new Date(row.clock_in).toLocaleTimeString() : '-'}</td>
                <td>${row.clock_out ? new Date(row.clock_out).toLocaleTimeString() : '-'}</td>
                <td><span class="tag tag-${row.status}">${row.status}</span></td>
            `;
            tbody.appendChild(tr);
        });
    } catch (err) {
        console.error("Load error:", err);
    }
}

loadAttendance();
setInterval(loadAttendance, 30000); // Refresh every 30s

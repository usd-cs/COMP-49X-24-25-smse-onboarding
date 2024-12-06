function markTaskComplete(checkbox) {
    const taskId = checkbox.getAttribute('data-task-id');
    fetch(`/mark-task-complete/${taskId}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            console.error(data.error || "error occurred");
        }
    });
}

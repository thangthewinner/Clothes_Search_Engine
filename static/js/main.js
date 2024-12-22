
// ...existing code...

document.querySelector('.text-search-section form')?.addEventListener('submit', function(e) {
    const submitBtn = this.querySelector('input[type="submit"]');
    submitBtn.value = 'Searching...';
    submitBtn.disabled = true;
});

// ...existing code...
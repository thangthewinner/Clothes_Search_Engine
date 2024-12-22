
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalClose = document.getElementById('modalClose');
    const modalSimilarity = document.getElementById('modalSimilarity');
    const modalTitle = document.getElementById('modalTitle');

    function openModal(imageSrc, similarity) {
        modalImage.src = imageSrc;
        modalSimilarity.textContent = `${similarity}% Match`;
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    // Add click listeners to all cards
    document.querySelectorAll('.card').forEach(card => {
        card.addEventListener('click', () => {
            const img = card.querySelector('.card-image');
            openModal(img.src, img.dataset.similarity);
        });
    });

    // Modal event listeners
    modalClose.addEventListener('click', closeModal);
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeModal();
    });

    // Keyboard support
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
        }
    });
});
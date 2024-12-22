document.addEventListener('DOMContentLoaded', () => {
    const themeSwitch = document.getElementById('themeSwitch');
    const fileInput = document.querySelector('input[type="file"]');
    const uploadText = document.querySelector('.upload-box p');
    const preview = document.getElementById('preview');
    const uploadBox = document.getElementById('uploadBox');
    const uploadAgain = document.getElementById('uploadAgain');
    const uploadControls = document.querySelector('.upload-controls');

    themeSwitch.addEventListener('click', handleThemeSwitch);
    fileInput.addEventListener('change', handleFileUpload);
    uploadAgain.addEventListener('click', () => fileInput.click());

    function handleThemeSwitch(e) {
        if (e.target.tagName === 'SPAN') {
            const theme = e.target.dataset.theme;
            document.documentElement.setAttribute('data-theme', theme);
            themeSwitch.querySelectorAll('span').forEach(span => span.classList.remove('active'));
            e.target.classList.add('active');
        }
    }

    function handleFileUpload(e) {
        const file = e.target.files[0];
        if (file) {
            uploadText.textContent = 'Click or drag image here';
            const reader = new FileReader();
            reader.onload = function(e) {
                preview.src = e.target.result;
                preview.style.display = 'block';
                uploadBox.classList.add('minimized');
                uploadControls.style.display = 'flex';
            }
            reader.readAsDataURL(file);
        }
    }

    const cards = document.querySelectorAll('.result-card');
    const modal = document.getElementById('imageModal');
    const modalImage = document.getElementById('modalImage');
    const modalSimilarity = document.getElementById('modalSimilarity');
    const modalClose = document.querySelector('.modal-close');
    const modalOverlay = document.querySelector('.modal-overlay');

    cards.forEach(card => {
        card.addEventListener('click', () => {
            const img = card.querySelector('.card-img');
            const similarity = img.dataset.similarity;
            openModal(img.src, similarity);
        });
    });

    function openModal(imageSrc, similarity) {
        modalImage.src = imageSrc;
        modalSimilarity.textContent = `${similarity}% Similar`;
        modal.classList.add('active');
        document.body.style.overflow = 'hidden';
    }

    function closeModal() {
        modal.classList.remove('active');
        document.body.style.overflow = '';
    }

    modalClose.addEventListener('click', closeModal);
    modalOverlay.addEventListener('click', closeModal);

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && modal.classList.contains('active')) {
            closeModal();
        }
    });
});
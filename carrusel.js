document.addEventListener('DOMContentLoaded', function() {
    const slides = document.querySelectorAll('.slider-container img');
    let currentSlide = 0;
    
    function nextSlide() {
        slides[currentSlide].classList.remove('active');
        
        currentSlide = (currentSlide + 1) % slides.length;
        
        slides[currentSlide].classList.add('active');
    }
    
    setInterval(nextSlide, 5000);
});
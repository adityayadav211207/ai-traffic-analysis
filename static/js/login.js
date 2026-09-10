/**
 * TrafficVision AI - Login Page Interactive Logic
 */

document.addEventListener("DOMContentLoaded", () => {
    // Password Toggle Visibility
    const passwordInput = document.getElementById("password");
    const toggleBtn = document.getElementById("togglePassword");
    const toggleIcon = document.getElementById("togglePasswordIcon");

    if (toggleBtn && passwordInput && toggleIcon) {
        toggleBtn.addEventListener("click", (e) => {
            e.preventDefault();
            const isPassword = passwordInput.getAttribute("type") === "password";
            
            if (isPassword) {
                passwordInput.setAttribute("type", "text");
                toggleIcon.classList.remove("fa-eye");
                toggleIcon.classList.add("fa-eye-slash");
            } else {
                passwordInput.setAttribute("type", "password");
                toggleIcon.classList.remove("fa-eye-slash");
                toggleIcon.classList.add("fa-eye");
            }
        });
    }

    // Demo Autofill Functionality
    const usernameInput = document.getElementById("usernameInput");
    const demoAdminBtn = document.getElementById("demoAdminBtn");
    const demoUserBtn = document.getElementById("demoUserBtn");
    const demoBtns = [demoAdminBtn, demoUserBtn];

    function highlightFill(inputElement) {
        inputElement.style.transition = "all 0.3s ease";
        inputElement.style.borderColor = "#3B82F6";
        inputElement.style.boxShadow = "0 0 0 3px rgba(59, 130, 246, 0.35)";
        
        setTimeout(() => {
            inputElement.style.borderColor = "";
            inputElement.style.boxShadow = "";
        }, 600);
    }

    if (demoAdminBtn && usernameInput && passwordInput) {
        demoAdminBtn.addEventListener("click", () => {
            demoBtns.forEach(btn => btn?.classList.remove("active-demo"));
            demoAdminBtn.classList.add("active-demo");
            
            usernameInput.value = "admin";
            passwordInput.value = "admin123";
            
            highlightFill(usernameInput);
            highlightFill(passwordInput);
            passwordInput.focus();
        });
    }

    if (demoUserBtn && usernameInput && passwordInput) {
        demoUserBtn.addEventListener("click", () => {
            demoBtns.forEach(btn => btn?.classList.remove("active-demo"));
            demoUserBtn.classList.add("active-demo");
            
            usernameInput.value = "user";
            passwordInput.value = "user123";
            
            highlightFill(usernameInput);
            highlightFill(passwordInput);
            passwordInput.focus();
        });
    }

    // Button submit feedback
    const loginForm = document.getElementById("loginForm");
    const submitBtn = document.getElementById("submitBtn");

    if (loginForm && submitBtn) {
        loginForm.addEventListener("submit", () => {
            submitBtn.disabled = true;
            submitBtn.innerHTML = `
                <i class="fa-solid fa-circle-notch fa-spin"></i>
                <span>Verifying Credentials...</span>
            `;
            submitBtn.style.opacity = "0.85";
        });
    }

    // Forgot Password and SSO alerts
    const forgotPasswordLink = document.getElementById("forgotPasswordLink");
    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener("click", (e) => {
            e.preventDefault();
            alert("For demo reset: Use 'admin' / 'admin123' or contact your system administrator.");
        });
    }

    // Google Modal Handling
    const googleBtn = document.getElementById("googleLoginBtn");
    const googleModal = document.getElementById("googleModal");
    const closeGoogleModalBtn = document.getElementById("closeGoogleModal");

    if (googleBtn && googleModal) {
        googleBtn.addEventListener("click", () => {
            googleModal.classList.add("show");
        });
    }

    if (closeGoogleModalBtn && googleModal) {
        closeGoogleModalBtn.addEventListener("click", () => {
            googleModal.classList.remove("show");
        });
    }

    if (googleModal) {
        // Close on clicking backdrop
        googleModal.addEventListener("click", (e) => {
            if (e.target === googleModal) {
                googleModal.classList.remove("show");
            }
        });

        // Close on ESC key
        document.addEventListener("keydown", (e) => {
            if (e.key === "Escape" && googleModal.classList.contains("show")) {
                googleModal.classList.remove("show");
            }
        });
    }
});
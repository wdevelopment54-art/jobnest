/* ============================================================
   Job Portal - Frontend interactions (Vanilla JS)
   ============================================================ */
(function () {
    'use strict';

    /* ---- Mobile navigation toggle ---- */
    var navToggle = document.querySelector('.nav-toggle');
    var navMenu = document.getElementById('navMenu');
    if (navToggle && navMenu) {
        navToggle.addEventListener('click', function () {
            navMenu.classList.toggle('open');
        });
        navMenu.querySelectorAll('a').forEach(function (link) {
            link.addEventListener('click', function () {
                navMenu.classList.remove('open');
            });
        });
    }

    /* ---- Auto-dismiss flash alerts ---- */
    document.querySelectorAll('.alert-dismissible').forEach(function (alert) {
        setTimeout(function () {
            alert.style.transition = 'opacity 0.4s ease';
            alert.style.opacity = '0';
            setTimeout(function () { alert.remove(); }, 400);
        }, 5000);
    });

    /* ---- Confirm dialogs via data-confirm attribute ---- */
    document.querySelectorAll('[data-confirm]').forEach(function (el) {
        el.addEventListener('submit', function (e) {
            if (!window.confirm(el.getAttribute('data-confirm'))) {
                e.preventDefault();
            }
        });
    });

    /* ---- Password visibility toggle ---- */
    document.querySelectorAll('[data-toggle-password]').forEach(function (btn) {
        btn.addEventListener('click', function () {
            var input = document.getElementById(btn.getAttribute('data-toggle-password'));
            if (!input) return;
            if (input.type === 'password') {
                input.type = 'text';
                btn.innerHTML = '<i class="fa-solid fa-eye-slash"></i>';
            } else {
                input.type = 'password';
                btn.innerHTML = '<i class="fa-solid fa-eye"></i>';
            }
        });
    });

    /* ---- Character counter for textareas with data-maxlength ---- */
    document.querySelectorAll('textarea[data-maxlength]').forEach(function (ta) {
        var max = parseInt(ta.getAttribute('data-maxlength'), 10);
        var counter = document.createElement('span');
        counter.className = 'char-counter small muted';
        ta.parentNode.appendChild(counter);
        var update = function () {
            var len = ta.value.length;
            counter.textContent = len + ' / ' + max;
            if (len > max) counter.style.color = 'var(--danger)';
            else counter.style.color = '';
        };
        ta.addEventListener('input', update);
        update();
    });

    /* ---- File input label update ---- */
    document.querySelectorAll('input[type="file"]').forEach(function (input) {
        input.addEventListener('change', function () {
            var label = input.parentNode.querySelector('.file-name');
            if (!label) {
                label = document.createElement('span');
                label.className = 'file-name small muted';
                input.parentNode.appendChild(label);
            }
            label.textContent = input.files.length ? input.files[0].name : '';
        });
    });

    /* ---- Sticky header shadow on scroll ---- */
    var navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function () {
            if (window.scrollY > 10) navbar.style.boxShadow = '0 4px 16px rgba(0,0,0,0.18)';
            else navbar.style.boxShadow = '0 2px 12px rgba(0,0,0,0.12)';
        });
    }

    /* ---- Toast notification system ---- */
    function showToast(message, type) {
        type = type || 'success';
        var container = document.getElementById('toastContainer');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toastContainer';
            container.className = 'toast-container';
            document.body.appendChild(container);
        }
        var toast = document.createElement('div');
        toast.className = 'toast toast-' + type;
        var icon = type === 'success' ? 'fa-circle-check'
            : type === 'error' ? 'fa-circle-exclamation'
                : type === 'info' ? 'fa-circle-info' : 'fa-circle-check';
        toast.innerHTML = '<i class="fa-solid ' + icon + '"></i><span>' + message + '</span>';
        container.appendChild(toast);
        requestAnimationFrame(function () { toast.classList.add('show'); });
        setTimeout(function () {
            toast.classList.remove('show');
            setTimeout(function () { toast.remove(); }, 350);
        }, 4500);
    }
    window.showToast = showToast;

    /* ---- Contact form client-side validation ---- */
    var contactForm = document.getElementById('contactForm');
    if (contactForm) {
        var emailRe = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        var phoneRe = /^[+0-9 ()-]{7,20}$/;

        function setError(field, msg) {
            var input = contactForm.querySelector('[name="' + field + '"]');
            if (!input) return;
            input.classList.add('is-invalid');
            var group = input.closest('.form-group');
            var existing = group ? group.querySelector('.error-text') : null;
            if (group && !existing) {
                var span = document.createElement('span');
                span.className = 'error-text';
                group.appendChild(span);
            }
            if (group) {
                var err = group.querySelector('.error-text');
                if (err) err.textContent = msg;
            }
        }
        function clearError(field) {
            var input = contactForm.querySelector('[name="' + field + '"]');
            if (!input) return;
            input.classList.remove('is-invalid');
            var group = input.closest('.form-group');
            if (group) {
                var err = group.querySelector('.error-text');
                if (err) err.remove();
            }
        }

        contactForm.addEventListener('submit', function (e) {
            var ok = true;
            var name = contactForm.name.value.trim();
            var email = contactForm.email.value.trim();
            var phone = contactForm.phone.value.trim();
            var subject = contactForm.subject.value.trim();
            var message = contactForm.message.value.trim();

            ['name', 'email', 'phone', 'subject', 'message'].forEach(clearError);

            if (name.length < 2) { setError('name', 'Please enter your full name.'); ok = false; }
            if (!emailRe.test(email)) { setError('email', 'Please enter a valid email address.'); ok = false; }
            if (phone && !phoneRe.test(phone)) { setError('phone', 'Please enter a valid phone number.'); ok = false; }
            if (subject.length < 3) { setError('subject', 'Subject is too short.'); ok = false; }
            if (message.length < 20) { setError('message', 'Message should be at least 20 characters.'); ok = false; }

            if (!ok) {
                e.preventDefault();
                showToast('Please correct the highlighted fields.', 'error');
                var firstInvalid = contactForm.querySelector('.is-invalid');
                if (firstInvalid) firstInvalid.focus();
            }
        });

        // Clear error on input
        contactForm.querySelectorAll('input, textarea').forEach(function (el) {
            el.addEventListener('input', function () {
                if (el.name) clearError(el.name);
            });
        });
    }
})();

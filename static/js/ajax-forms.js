/**
 * Global AJAX Form Handler
 * Automatically converts form submissions to AJAX, eliminating page reloads
 * throughout the application
 */

document.addEventListener('DOMContentLoaded', function() {
  // Helper to get CSRF token
  function getCsrfToken() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
           document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1];
  }

  function getFormAction(form) {
    const actionAttr = form.getAttribute('action');
    return actionAttr && actionAttr.trim() ? actionAttr : window.location.pathname;
  }

  // Intercept all form submissions
  document.addEventListener('submit', function(e) {
    const form = e.target;
    const method = form.method.toUpperCase();
    const isGetForm = method === 'GET';

    // Skip forms that are explicitly marked to not use AJAX
    if (form.classList.contains('no-ajax')) return;

    // Skip file upload forms with enctype multipart (these need special handling per-form)
    if (form.enctype === 'multipart/form-data' && form.classList.contains('no-ajax-file')) {
      return;
    }

    // For GET forms (search/filter), use AJAX with history state
    if (isGetForm) {
      e.preventDefault();
      handleGetFormAjax(form);
      return;
    }

    // For POST forms, check if we should handle as AJAX
    const action = getFormAction(form);
    
    // Don't intercept file uploads that aren't marked for AJAX handling
    if (form.enctype === 'multipart/form-data' && !form.classList.contains('force-ajax-file')) {
      return;
    }

    e.preventDefault();
    handlePostFormAjax(form);
  }, true); // Use capture phase to intercept before other listeners

  function handlePostFormAjax(form) {
    const action = getFormAction(form);
    const method = form.method.toUpperCase();
    const formData = new FormData(form);
    const csrfToken = getCsrfToken();

    // Add spinner/loading state
    const submitButton = form.querySelector('button[type="submit"]');
    if (submitButton) {
      submitButton.disabled = true;
      submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Processing...';
    }

    fetch(action, {
      method: method,
      headers: {
        'X-CSRFToken': csrfToken,
        'X-Requested-With': 'XMLHttpRequest',
      },
      body: formData,
    })
    .then(response => {
      // Handle redirects
      if (response.redirected) {
        window.location.href = response.url;
        return null;
      }
      return response.json().catch(() => response.text());
    })
    .then(data => {
      if (data === null) return; // Already handled redirect

      // Re-enable submit button
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.innerHTML = submitButton.dataset.originalText || 'Submit';
      }

      // Handle JSON response
      if (typeof data === 'object') {
        if (data.ok === false && data.redirect_url) {
          // Special redirect case
          window.location.href = data.redirect_url;
          return;
        }

        if (data.redirect_url) {
          window.location.href = data.redirect_url;
          return;
        }

        // Show success message if form has data-success-message
        const successMsg = form.dataset.successMessage;
        if (successMsg && !window.location.href.includes('delete')) {
          showAlert('success', successMsg);
        }

        // Check for form errors
        if (data.errors) {
          displayFormErrors(form, data.errors);
          return;
        }

        // If response has ok:true and no redirect, assume success and reset form
        if (data.ok === true) {
          form.reset();
          showAlert('success', form.dataset.successMessage || 'Success!');
        }
      } else if (typeof data === 'string' && data.includes('redirect')) {
        // HTML response with redirect info
        const redirectMatch = data.match(/href="([^"]+)"/);
        if (redirectMatch) {
          window.location.href = redirectMatch[1];
        }
      }
    })
    .catch(error => {
      // Re-enable submit button
      if (submitButton) {
        submitButton.disabled = false;
        submitButton.innerHTML = submitButton.dataset.originalText || 'Submit';
      }

      console.error('Form submission error:', error);
      showAlert('danger', 'An error occurred. Please try again.');
    });
  }

  function handleGetFormAjax(form) {
    const action = getFormAction(form);
    const formData = new FormData(form);
    const queryString = new URLSearchParams(formData).toString();
    const targetId = form.dataset.targetId;
    const requestUrl = queryString ? `${action}?${queryString}` : action;

    // Show loading state if target exists
    if (targetId) {
      const target = document.getElementById(targetId);
      if (target) {
        target.innerHTML = '<div class="text-center text-muted py-4"><i class="bi bi-hourglass-split"></i> Loading...</div>';
      }
    }

    fetch(requestUrl, {
      method: 'GET',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
      },
    })
    .then(response => response.text())
    .then(html => {
      // Update URL without page reload
      window.history.pushState({ path: requestUrl }, '', requestUrl);

      // Update target element if specified
      if (targetId) {
        const target = document.getElementById(targetId);
        if (target) {
          // Clear completely before inserting new content to prevent duplication
          target.innerHTML = '';
          target.innerHTML = html;
          // Trigger any event handlers on new content
          document.dispatchEvent(new CustomEvent('ajax-content-loaded', {
            detail: { html, form }
          }));
        }
      } else {
        // Fallback: show in alert or console
        console.log('Search results loaded');
      }
    })
    .catch(error => {
      console.error('Search error:', error);
      showAlert('danger', 'Search failed. Please try again.');
    });
  }

  function displayFormErrors(form, errors) {
    // Clear previous errors
    form.querySelectorAll('.invalid-feedback').forEach(el => el.remove());
    form.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));

    // Display new errors
    Object.keys(errors).forEach(fieldName => {
      const field = form.querySelector(`[name="${fieldName}"]`);
      if (field) {
        field.classList.add('is-invalid');
        const errorMsg = document.createElement('div');
        errorMsg.className = 'invalid-feedback d-block';
        
        const errors_list = errors[fieldName];
        if (Array.isArray(errors_list)) {
          errorMsg.textContent = errors_list.map(e => e.message || e).join(', ');
        } else {
          errorMsg.textContent = errors_list;
        }
        
        field.parentNode.appendChild(errorMsg);
      }
    });
  }

  function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alertDiv.style.cssText = 'top: 80px; right: 20px; z-index: 9999; max-width: 500px;';
    alertDiv.innerHTML = `
      ${message}
      <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    document.body.appendChild(alertDiv);

    // Auto dismiss after 5 seconds
    setTimeout(() => {
      alertDiv.classList.remove('show');
      setTimeout(() => alertDiv.remove(), 150);
    }, 5000);
  }
});

// Handle browser back button to reload content if needed
window.addEventListener('popstate', function(e) {
  if (e.state && e.state.path) {
    window.location.href = e.state.path;
  }
});

// TREMHUB — Main JavaScript

// ========================
// PWA Install Prompt
// ========================
let deferredPrompt = null;

window.addEventListener('beforeinstallprompt', (e) => {
  e.preventDefault();
  deferredPrompt = e;
  const btn = document.getElementById('installBtn');
  if (btn) btn.classList.remove('d-none');
});

function installPWA() {
  if (!deferredPrompt) return;
  deferredPrompt.prompt();
  deferredPrompt.userChoice.then((result) => {
    if (result.outcome === 'accepted') {
      console.log('TREMHUB installed!');
    }
    deferredPrompt = null;
    const btn = document.getElementById('installBtn');
    if (btn) btn.classList.add('d-none');
  });
}

window.addEventListener('appinstalled', () => {
  deferredPrompt = null;
  const btn = document.getElementById('installBtn');
  if (btn) btn.classList.add('d-none');
});

// ========================
// Service Worker Registration
// ========================
if ('serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/static/sw.js')
      .then(reg => console.log('SW registered:', reg.scope))
      .catch(err => console.log('SW failed:', err));
  });
}

// ========================
// Auto-dismiss alerts
// ========================
document.addEventListener('DOMContentLoaded', () => {
  const alerts = document.querySelectorAll('.alert');
  alerts.forEach(alert => {
    setTimeout(() => {
      const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
      if (bsAlert) bsAlert.close();
    }, 5000);
  });

  // Activate nav links based on current path
  const currentPath = window.location.pathname;
  document.querySelectorAll('.nav-link, .nav-links a, .nav-mobile a').forEach(link => {
    if (link.getAttribute('href') === currentPath) {
      link.classList.add('active');
    }
  });
});


// ========================
// Tweet-style compose helpers
// ========================
document.addEventListener('DOMContentLoaded', () => {
  const hasSelectedMedia = (form) => {
    if (!form) return false;
    const imageInput = form.querySelector('.tweet-image-input');
    const videoInput = form.querySelector('.tweet-video-input');
    const cameraInput = form.querySelector('.tweet-camera-input');
    const hasImage = Boolean(imageInput && imageInput.files && imageInput.files[0]);
    const hasVideo = Boolean(videoInput && videoInput.files && videoInput.files[0]);
    const hasCameraImage = Boolean(cameraInput && cameraInput.files && cameraInput.files[0]);
    return hasImage || hasVideo || hasCameraImage;
  };

  const updateComposeCounter = (form) => {
    if (!form) return;
    const textarea = form.querySelector('.tweet-compose-input');
    const counter = form.querySelector('.tweet-char-counter');
    const submitButton = form.querySelector('.tweet-post-btn');
    if (!textarea || !counter || !submitButton) return;

    const maxLength = Number(textarea.getAttribute('data-maxlength') || textarea.getAttribute('maxlength')) || 250;
    const currentLength = textarea.value.length;
    const remaining = maxLength - currentLength;
    const progress = Math.min(140, (currentLength / maxLength) * 100);

    counter.textContent = String(remaining);
    counter.style.setProperty('--progress', String(progress));
    counter.classList.toggle('over-limit', remaining < 0);
    counter.classList.toggle('near-limit', remaining >= 0 && remaining <= 20);
    submitButton.disabled = (currentLength === 0 && !hasSelectedMedia(form)) || remaining < 0;
  };

  document.querySelectorAll('.tweet-compose-form').forEach((form) => {
    const textarea = form.querySelector('.tweet-compose-input');
    const fileInput = form.querySelector('.tweet-image-input');
    const videoInput = form.querySelector('.tweet-video-input');
    const cameraInput = form.querySelector('.tweet-camera-input');
    const previewWrap = form.querySelector('.tweet-compose-preview');
    const previewImage = form.querySelector('.tweet-compose-preview-image');
    const previewVideo = form.querySelector('.tweet-compose-preview-video');
    const previewRemove = form.querySelector('.tweet-compose-preview-remove');
    const mediaButton = form.querySelector('[data-image-source="gallery"]');
    const videoButton = form.querySelector('[data-image-source="video"]');
    const cameraButton = form.querySelector('[data-image-source="camera"]');

    const clearPreview = () => {
      if (!previewWrap || !previewImage || !previewVideo) return;
      if (fileInput) fileInput.value = '';
      if (videoInput) videoInput.value = '';
      if (cameraInput) cameraInput.value = '';
      previewImage.removeAttribute('src');
      previewVideo.pause();
      previewVideo.removeAttribute('src');
      previewVideo.hidden = true;
      previewImage.hidden = false;
      previewWrap.hidden = true;
      updateComposeCounter(form);
    };

    const getSelectedMediaFile = () => {
      const cameraFile = cameraInput && cameraInput.files && cameraInput.files[0];
      if (cameraFile && cameraFile.type.startsWith('image/')) {
        return { file: cameraFile, type: 'image' };
      }

      const galleryFile = fileInput && fileInput.files && fileInput.files[0];
      if (galleryFile && galleryFile.type.startsWith('image/')) {
        return { file: galleryFile, type: 'image' };
      }

      const uploadedVideo = videoInput && videoInput.files && videoInput.files[0];
      if (uploadedVideo && uploadedVideo.type.startsWith('video/')) {
        return { file: uploadedVideo, type: 'video' };
      }

      return null;
    };

    const updatePreview = () => {
      if (!previewWrap || !previewImage || !previewVideo) return;
      const media = getSelectedMediaFile();
      if (!media || !media.file) {
        previewImage.removeAttribute('src');
        previewVideo.pause();
        previewVideo.removeAttribute('src');
        previewVideo.hidden = true;
        previewImage.hidden = false;
        previewWrap.hidden = true;
        updateComposeCounter(form);
        return;
      }

      if (media.type === 'video') {
        previewImage.removeAttribute('src');
        previewImage.hidden = true;
        previewVideo.src = URL.createObjectURL(media.file);
        previewVideo.hidden = false;
        previewWrap.hidden = false;
        updateComposeCounter(form);
        return;
      }

      const reader = new FileReader();
      reader.onload = (e) => {
        previewVideo.pause();
        previewVideo.removeAttribute('src');
        previewVideo.hidden = true;
        previewImage.src = e.target.result;
        previewImage.hidden = false;
        previewWrap.hidden = false;
        updateComposeCounter(form);
      };
      reader.readAsDataURL(media.file);
    };

    if (textarea) {
      textarea.addEventListener('input', () => updateComposeCounter(form));
      textarea.addEventListener('keyup', () => updateComposeCounter(form));
      textarea.addEventListener('change', () => updateComposeCounter(form));
      updateComposeCounter(form);
    }

    if (fileInput) {
      fileInput.addEventListener('change', () => {
        if (videoInput) videoInput.value = '';
        if (cameraInput) cameraInput.value = '';
        updatePreview();
      });
    }

    if (videoInput) {
      videoInput.addEventListener('change', () => {
        if (fileInput) fileInput.value = '';
        if (cameraInput) cameraInput.value = '';
        updatePreview();
      });
    }

    if (cameraInput) {
      cameraInput.addEventListener('change', () => {
        if (fileInput) fileInput.value = '';
        if (videoInput) videoInput.value = '';
        updatePreview();
      });
    }

    if (previewRemove) {
      previewRemove.addEventListener('click', clearPreview);
    }

    if (mediaButton && fileInput) {
      mediaButton.addEventListener('click', () => {
        fileInput.removeAttribute('capture');
        fileInput.click();
      });
    }

    if (videoButton && videoInput) {
      videoButton.addEventListener('click', () => {
        videoInput.click();
      });
    }

    if (cameraButton) {
      cameraButton.addEventListener('click', () => {
        if (fileInput) fileInput.value = '';
      });
    }
  });

  // Fallback delegated updates for paste/auto-fill/IME edge cases.
  document.addEventListener('input', (event) => {
    if (!event.target.matches('.tweet-compose-input')) return;
    updateComposeCounter(event.target.closest('.tweet-compose-form'));
  });

  document.addEventListener('change', (event) => {
    if (!event.target.matches('.tweet-compose-input')) return;
    updateComposeCounter(event.target.closest('.tweet-compose-form'));
  });
});

document.addEventListener('click', async (event) => {
  const shareButton = event.target.closest('.tweet-share-btn');
  if (!shareButton) return;

  const title = shareButton.dataset.shareTitle || document.title;
  const url = shareButton.dataset.shareUrl || window.location.href;

  try {
    if (navigator.share) {
      await navigator.share({ title, url });
    } else if (navigator.clipboard) {
      await navigator.clipboard.writeText(url);
      alert('Link copied to clipboard.');
    } else {
      window.prompt('Copy this link', url);
    }
  } catch (error) {
    console.log('Share cancelled or failed:', error);
  }
});

document.addEventListener('DOMContentLoaded', () => {
  const getCookie = (name) => {
    const cookieValue = document.cookie
      .split('; ')
      .find((row) => row.startsWith(`${name}=`));
    return cookieValue ? decodeURIComponent(cookieValue.split('=')[1]) : '';
  };

  const getCsrfToken = (form) => {
    if (form) {
      const tokenInput = form.querySelector('input[name="csrfmiddlewaretoken"]');
      if (tokenInput && tokenInput.value) return tokenInput.value;
    }
    return getCookie('csrftoken');
  };

  const escapeHtml = (value) => {
    return String(value || '')
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  };

  const formatCommentDate = (iso) => {
    if (!iso) return '';
    const date = new Date(iso);
    if (Number.isNaN(date.getTime())) return '';
    return new Intl.DateTimeFormat(undefined, {
      month: 'short',
      day: 'numeric',
      hour: 'numeric',
      minute: '2-digit',
    }).format(date);
  };

  const updateLikeButtonUI = (button, liked, likeCount) => {
    if (!button) return;
    const icon = button.querySelector('i.bi');
    const label = button.querySelector('span');
    const count = button.querySelector('.tweet-count');

    button.classList.toggle('tweet-action-liked', Boolean(liked));
    if (icon) {
      icon.classList.toggle('bi-heart-fill', Boolean(liked));
      icon.classList.toggle('bi-heart', !liked);
    }
    if (label) label.textContent = liked ? 'Liked' : 'Like';
    if (count) count.textContent = String(likeCount);
  };

  const updateReplyCounts = (nextCount) => {
    document.querySelectorAll('a[href="#replies"] .tweet-count').forEach((el) => {
      el.textContent = String(nextCount);
    });
  };

  const updateCommentLikeButtonUI = (button, liked, likeCount) => {
    if (!button) return;
    const icon = button.querySelector('i.bi');
    const label = button.querySelector('span');
    const count = button.querySelector('.tweet-count');

    button.classList.toggle('tweet-comment-action-liked', Boolean(liked));
    if (icon) {
      icon.classList.toggle('bi-heart-fill', Boolean(liked));
      icon.classList.toggle('bi-heart', !liked);
    }
    if (label) label.textContent = liked ? 'Liked' : 'Like';
    if (count) count.textContent = String(likeCount);
  };

  const focusReplyComposer = (commentButton) => {
    const composer = document.querySelector('.tweet-async-comment-form');
    if (!composer) return;

    const textarea = composer.querySelector('textarea[name="content"]');
    if (!textarea) return;

    const author = commentButton?.dataset.commentAuthor || '';
    const prefix = author ? `@${author} ` : '';
    if (!textarea.value.trim()) {
      textarea.value = prefix;
    } else if (prefix && !textarea.value.includes(prefix)) {
      textarea.value = `${prefix}${textarea.value}`.trim();
    }

    textarea.focus();
    textarea.setSelectionRange(textarea.value.length, textarea.value.length);
    composer.scrollIntoView({ behavior: 'smooth', block: 'center' });
  };

  document.querySelectorAll('.tweet-like-form').forEach((form) => {
    const button = form.querySelector('button[type="submit"]');
    if (!button) return;

    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (button.disabled) return;
      button.disabled = true;

      try {
        const response = await fetch(form.action, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken(form),
          },
        });

        if (!response.ok) throw new Error('Like request failed');
        const data = await response.json();
        updateLikeButtonUI(button, data.liked, data.like_count);
      } catch (error) {
        console.log(error);
      } finally {
        button.disabled = false;
      }
    });
  });

  document.querySelectorAll('.tweet-post-delete-form').forEach((form) => {
    form.addEventListener('submit', async (event) => {
      event.preventDefault();
      if (!window.confirm('Delete this post?')) return;

      try {
        const response = await fetch(form.action, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken(form),
          },
        });

        if (!response.ok) throw new Error('Delete request failed');
        const data = await response.json();
        if (!data.deleted) return;

        const card = form.closest('[data-post-slug]');
        if (card) card.remove();

        if (window.location.pathname.includes('/blog/') && window.location.pathname !== '/blog/') {
          window.location.href = data.redirect_url || '/blog/';
        }
      } catch (error) {
        console.log(error);
      }
    });
  });

  document.addEventListener('submit', async (event) => {
    const likeForm = event.target.closest('.tweet-comment-like-form');
    if (likeForm) {
      event.preventDefault();
      const button = likeForm.querySelector('button[type="submit"], button.tweet-comment-like-button');
      if (!button || button.disabled) return;
      button.disabled = true;
      
      try {
        const response = await fetch(likeForm.action, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken(likeForm),
          },
        });
        
        if (!response.ok) throw new Error('Comment like request failed');
        const data = await response.json();
        updateCommentLikeButtonUI(button, data.liked, data.like_count);
      } catch (error) {
        console.log(error);
      } finally {
        button.disabled = false;
      }
      return;
    }
    
    const deleteForm = event.target.closest('.tweet-comment-delete-form');
    if (deleteForm) {
      event.preventDefault();
      try {
        await submitCommentDelete(deleteForm, true);
      } catch (error) {
        console.log(error);
      }
    }
  });

  const postInsightsModalEl = document.getElementById('postInsightsModal');
  const postInsightsModal = (postInsightsModalEl && window.bootstrap)
    ? new bootstrap.Modal(postInsightsModalEl)
    : null;

  const submitPostActionForm = async (form) => {
    if (!form) return null;
    const response = await fetch(form.action, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': getCsrfToken(form),
      },
    });

    if (!response.ok) {
      throw new Error('Post action failed');
    }

    return response.json();
  };

  const submitCommentDelete = async (deleteForm, askConfirm = true) => {
    if (!deleteForm) return;
    if (askConfirm && !window.confirm('Delete this reply?')) return;

    const response = await fetch(deleteForm.action, {
      method: 'POST',
      headers: {
        'X-Requested-With': 'XMLHttpRequest',
        'X-CSRFToken': getCsrfToken(deleteForm),
      },
    });

    if (!response.ok) throw new Error('Comment delete failed');
    const data = await response.json();
    if (!data.deleted) return;

    const comment = deleteForm.closest('[data-comment-id]');
    if (comment) comment.remove();
    updateReplyCounts(data.comment_count || 0);

    const list = document.getElementById('tweet-comment-list');
    const existingEmptyState = document.getElementById('tweet-no-replies');
    if (list && !list.querySelector('[data-comment-id]') && !existingEmptyState) {
      const placeholder = document.createElement('p');
      placeholder.className = 'text-muted mb-0';
      placeholder.id = 'tweet-no-replies';
      placeholder.textContent = 'No replies yet.';
      list.insertAdjacentElement('afterend', placeholder);
    }
  };

  document.addEventListener('click', async (event) => {
    const insightsButton = event.target.closest('.tweet-post-insights-btn');
    if (insightsButton) {
      const card = insightsButton.closest('[data-post-slug]');
      if (!card) return;

      const titleEl = document.getElementById('postInsightsTitle');
      const viewsEl = document.getElementById('postInsightsViews');
      const likesEl = document.getElementById('postInsightsLikes');
      const repliesEl = document.getElementById('postInsightsReplies');

      if (titleEl) {
        titleEl.textContent = `${card.dataset.postTitle || 'This post'} · ${card.dataset.postCreated || ''}`;
      }
      if (viewsEl) viewsEl.textContent = card.dataset.postViews || '0';
      if (likesEl) likesEl.textContent = card.dataset.postLikes || '0';
      if (repliesEl) repliesEl.textContent = card.dataset.postComments || '0';

      if (postInsightsModal) {
        postInsightsModal.show();
      }
      return;
    }

    const menuDeleteButton = event.target.closest('.tweet-menu-delete-btn');
    if (menuDeleteButton) {
      const card = menuDeleteButton.closest('[data-post-slug]');
      const deleteForm = card ? card.querySelector('.tweet-post-delete-form') : null;
      if (deleteForm) {
        deleteForm.dispatchEvent(new Event('submit', { bubbles: true, cancelable: true }));
      }
      return;
    }

    const hideButton = event.target.closest('.tweet-menu-hide-btn');
    if (hideButton) {
      const card = hideButton.closest('[data-post-slug]');
      const hideForm = card ? card.querySelector('.tweet-post-hide-form') : null;
      if (!hideForm) return;
      if (!window.confirm('Hide this post from your feed?')) return;

      try {
        const data = await submitPostActionForm(hideForm);
        if (data && data.hidden && card) {
          card.remove();
        }
      } catch (error) {
        console.log(error);
      }
      return;
    }

    const reportButton = event.target.closest('.tweet-menu-report-btn');
    if (reportButton) {
      const card = reportButton.closest('[data-post-slug]');
      const reportForm = card ? card.querySelector('.tweet-post-report-form') : null;
      if (!reportForm) return;
      if (!window.confirm('Report this post for review?')) return;

      try {
        const data = await submitPostActionForm(reportForm);
        if (data && data.reported) {
          alert(data.message || 'Report submitted.');
        }
      } catch (error) {
        console.log(error);
      }
      return;
    }

    const commentDeleteButton = event.target.closest('.tweet-comment-menu-delete-btn');
    if (commentDeleteButton) {
      const commentId = commentDeleteButton.dataset.commentId || commentDeleteButton.closest('[data-comment-id]')?.dataset.commentId;
      const comment = commentId
        ? document.querySelector(`[data-comment-id="${commentId}"]`)
        : commentDeleteButton.closest('[data-comment-id]');
      const deleteForm = comment
        ? comment.querySelector('.tweet-comment-delete-form')
        : (commentId ? document.querySelector(`.tweet-comment-delete-form[action*="/blog/comment/${commentId}/delete/"]`) : null);
      if (!deleteForm) return;

      try {
        await submitCommentDelete(deleteForm, true);
      } catch (error) {
        console.log(error);
      }
      return;
    }

    const commentReplyButton = event.target.closest('.tweet-comment-reply-btn, .tweet-comment-menu-reply-btn');
    if (commentReplyButton) {
      focusReplyComposer(commentReplyButton);
    }
  });

  const commentForm = document.querySelector('.tweet-async-comment-form');
  if (commentForm) {
    commentForm.addEventListener('submit', async (event) => {
      event.preventDefault();

      const submitButton = commentForm.querySelector('button[type="submit"], input[type="submit"]');
      const textarea = commentForm.querySelector('textarea[name="content"]');
      const list = document.getElementById('tweet-comment-list');
      const emptyState = document.getElementById('tweet-no-replies');

      if (!textarea || !textarea.value.trim()) return;
      if (submitButton) submitButton.disabled = true;

      try {
        const response = await fetch(window.location.href, {
          method: 'POST',
          headers: {
            'X-Requested-With': 'XMLHttpRequest',
            'X-CSRFToken': getCsrfToken(commentForm),
          },
          body: new FormData(commentForm),
        });

        if (!response.ok) throw new Error('Comment request failed');
        const data = await response.json();
        if (!data.ok || !data.comment) return;

        if (emptyState) emptyState.remove();

        const postCard = document.querySelector('[data-post-slug]');
        const postAuthor = postCard ? postCard.dataset.postAuthor || '' : '';
        const isSameAuthorReply = Boolean(postAuthor && data.comment.author_username === postAuthor);

        const wrapper = document.createElement('div');
        wrapper.className = `tweet-comment mb-3${isSameAuthorReply ? ' tweet-comment-thread' : ''}`;
        wrapper.setAttribute('data-comment-id', String(data.comment.id));
        wrapper.setAttribute('data-comment-author', data.comment.author_username || '');
        wrapper.setAttribute('data-comment-name', data.comment.author_name || '');
        wrapper.innerHTML = `
          <div class="d-flex gap-3">
            <div class="tweet-thread-avatar-wrap tweet-thread-avatar-wrap-comment${isSameAuthorReply ? ' tweet-thread-avatar-wrap-comment-thread' : ''}">
            <div class="tweet-avatar tweet-avatar-sm">
              ${data.comment.author_photo ? `<img src="${escapeHtml(data.comment.author_photo)}" alt="${escapeHtml(data.comment.author_name)}">` : `<span>${escapeHtml((data.comment.author_name || '?').slice(0, 1).toUpperCase())}</span>`}
            </div>
            ${isSameAuthorReply ? '<span class="tweet-thread-line"></span>' : ''}
            </div>
            <div class="flex-grow-1">
              <div class="d-flex align-items-start gap-2 flex-wrap">
                <div class="flex-grow-1 d-flex align-items-center gap-2 flex-wrap" style="min-width:0;">
                  <span class="fw-semibold text-dark">${escapeHtml(data.comment.author_name)}</span>
                  <span class="tweet-handle">@${escapeHtml(data.comment.author_username)}</span>
                  <span class="tweet-meta">${escapeHtml(formatCommentDate(data.comment.created_at))}</span>
                </div>
                <div class="dropdown tweet-comment-menu ms-auto">
                  <button class="btn tweet-comment-menu-toggle" type="button" data-bs-toggle="dropdown" aria-expanded="false" aria-label="Reply options">
                    <i class="bi bi-three-dots"></i>
                  </button>
                  <ul class="dropdown-menu dropdown-menu-end tweet-post-menu-list tweet-comment-menu-list">
                    <li>
                      <button type="button" class="dropdown-item text-danger tweet-comment-menu-delete-btn" data-comment-id="${data.comment.id}">
                        <i class="bi bi-trash me-2"></i>Delete Reply
                      </button>
                    </li>
                    <li>
                      <button type="button" class="dropdown-item tweet-comment-menu-reply-btn" data-comment-author="${escapeHtml(data.comment.author_username)}">
                        <i class="bi bi-reply me-2"></i>Reply
                      </button>
                    </li>
                  </ul>
                </div>
              </div>
              <div class="tweet-comment-body mt-1">${escapeHtml(data.comment.content).replace(/\n/g, '<br>')}</div>
              <div class="tweet-comment-actions mt-2">
                <button type="button" class="tweet-comment-action tweet-comment-reply-btn" data-comment-author="${escapeHtml(data.comment.author_username)}">
                  <i class="bi bi-reply"></i>
                  <span>Reply</span>
                </button>
                <form method="post" action="/blog/comment/${data.comment.id}/like/" class="d-inline tweet-comment-like-form">
                  <input type="hidden" name="csrfmiddlewaretoken" value="${escapeHtml(getCsrfToken(commentForm))}">
                  <button type="submit" class="tweet-comment-action tweet-comment-like-button">
                    <i class="bi bi-heart"></i>
                    <span>Like</span>
                    <span class="tweet-count">0</span>
                  </button>
                </form>
              </div>
            </div>
          </div>
          <form method="post" action="/blog/comment/${data.comment.id}/delete/" class="d-none tweet-comment-delete-form">
            <input type="hidden" name="csrfmiddlewaretoken" value="${escapeHtml(getCsrfToken(commentForm))}">
          </form>
        `;

        if (list) {
          list.prepend(wrapper);
        }

        textarea.value = '';
        updateReplyCounts(data.comment_count || 0);
      } catch (error) {
        console.log(error);
      } finally {
        if (submitButton) submitButton.disabled = false;
      }
    });
  }
});


  // Scroll → tighten the glass
  const nav = document.getElementById('mainNav');
  if (nav) {
    window.addEventListener('scroll', () => {
      nav.classList.toggle('scrolled', window.scrollY > 40);
    }, { passive: true });
  }
 
  // Hamburger toggle
  const btn = document.getElementById('hamburger');
  const menu = document.getElementById('mobileMenu');
  if (btn && menu) {
    const syncMenuState = (isOpen) => {
      btn.classList.toggle('open', isOpen);
      menu.classList.toggle('open', isOpen);
      btn.setAttribute('aria-expanded', String(isOpen));
    };

    btn.addEventListener('click', () => {
      syncMenuState(!menu.classList.contains('open'));
    });
 
    // Close mobile menu on link click
    menu.querySelectorAll('a').forEach(a => a.addEventListener('click', () => {
      syncMenuState(false);
    }));

    window.addEventListener('resize', () => {
      if (window.innerWidth >= 992) {
        syncMenuState(false);
      }
    }, { passive: true });
  }
import re

# Fix businesses list template
with open('templates/businesses/list.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the structure
old_pattern = '''      <div class="col-md-2">
        <button type="submit" class="btn btn-trem w-100">Search</button>
      </div>
    </form>
  </div>

  <!-- Results count -->
  <div class="d-flex justify-content-between align-items-center mb-3">
    <small class="text-muted">
      {{ businesses|length }} business{{ businesses|length|pluralize:"es" }} found
      {% if query or selected_category or selected_branch %}
        <a href="{% url 'businesses:list' %}" class="ms-2 text-trem">Clear filters</a>
      {% endif %}
    </small>
    {% if user.is_authenticated %}
    <a href="{% url 'businesses:create' %}" class="btn btn-trem btn-sm">
      <i class="bi bi-plus-lg me-1"></i>Add Business
    </a>
    {% endif %}
  </div>

  <!-- Grid -->
  <div id="business-results">'''

new_pattern = '''      <div class="col-md-2">
        <button type="submit" class="btn btn-trem w-100">Search</button>
      </div>
    </form>
  </div>

  <!-- Results and Grid (inside target for AJAX) -->
  <div id="business-results">
    <!-- Results count -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <small class="text-muted">
        {{ businesses|length }} business{{ businesses|length|pluralize:"es" }} found
        {% if query or selected_category or selected_branch %}
          <a href="{% url 'businesses:list' %}" class="ms-2 text-trem">Clear filters</a>
        {% endif %}
      </small>
      {% if user.is_authenticated %}
      <a href="{% url 'businesses:create' %}" class="btn btn-trem btn-sm">
        <i class="bi bi-plus-lg me-1"></i>Add Business
      </a>
      {% endif %}
    </div>

    <!-- Grid -->'''

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    with open('templates/businesses/list.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Fixed businesses list template")
else:
    print("! Pattern not found in businesses list template")

# Fix members list template
with open('templates/accounts/members.html', 'r', encoding='utf-8') as f:
    content = f.read()

old_pattern2 = '''      <div class="col-md-2">
        <button type="submit" class="btn btn-trem w-100">Search
        </button>
      </div>
    </form>
  </div>

  <!-- Results count -->
  <div class="d-flex justify-content-between align-items-center mb-3">
    <small class="text-muted">
      {{ profiles|length }} member{{ profiles|length|pluralize }} found
      {% if query or selected_branch or selected_unit %}
        <a href="{% url 'accounts:members' %}" class="ms-2 text-trem">Clear filters</a>
      {% endif %}
    </small>
  </div>

  <!-- Members Grid -->
  <div id="members-results">'''

new_pattern2 = '''      <div class="col-md-2">
        <button type="submit" class="btn btn-trem w-100">Search
        </button>
      </div>
    </form>
  </div>

  <!-- Results and Members Grid (inside target for AJAX) -->
  <div id="members-results">
    <!-- Results count -->
    <div class="d-flex justify-content-between align-items-center mb-3">
      <small class="text-muted">
        {{ profiles|length }} member{{ profiles|length|pluralize }} found
        {% if query or selected_branch or selected_unit %}
          <a href="{% url 'accounts:members' %}" class="ms-2 text-trem">Clear filters</a>
        {% endif %}
      </small>
    </div>

    <!-- Members Grid -->'''

if old_pattern2 in content:
    content = content.replace(old_pattern2, new_pattern2)
    with open('templates/accounts/members.html', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✓ Fixed members list template")
else:
    print("! Pattern not found in members list template")

print("\nDone!")

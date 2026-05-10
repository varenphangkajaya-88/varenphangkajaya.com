// ═══════════════════════════════════════════════════════
// JOURNAL LOADER
// Fetches markdown files from journals/ and renders to HTML
// ═══════════════════════════════════════════════════════

(function() {
  'use strict';

  let JOURNAL_FILES = [];

  function parseMarkdown(md) {
    if (!md) return '';
    let html = md;
    html = html.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/(?<!\*)\*([^*]+)\*(?!\*)/g, '<em>$1</em>');
    html = html.replace(/^### (.+)$/gm, '<h3>$1</h3>');
    html = html.replace(/^## (.+)$/gm, '<h2>$1</h2>');

    const lines = html.split('\n');
    const out = [];
    let inOl = false;
    let olStart = null;

    for (const line of lines) {
      const m = line.match(/^(\d+)\.\s+(.+)$/);
      if (m) {
        if (!inOl) {
          olStart = parseInt(m[1]);
          out.push(`<ol${olStart !== 1 ? ` start="${olStart}"` : ''}>`);
          inOl = true;
        }
        out.push(`<li>${m[2]}</li>`);
      } else {
        if (inOl) {
          out.push('</ol>');
          inOl = false;
        }
        out.push(line);
      }
    }
    if (inOl) out.push('</ol>');
    html = out.join('\n');

    const blocks = html.split(/\n\s*\n/);
    html = blocks.map(b => {
      const t = b.trim();
      if (!t) return '';
      if (/^<(h[1-6]|ol|ul|p|div|blockquote)/.test(t)) return t;
      return `<p>${t.replace(/\n/g, '<br>')}</p>`;
    }).join('\n');

    return html;
  }

  function parseArticle(text) {
    const fmMatch = text.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
    if (!fmMatch) return { meta: {}, body: text };

    const meta = {};
    const fmText = fmMatch[1];
    const body = fmMatch[2].trim();

    let currentObj = null;
    for (const line of fmText.split('\n')) {
      const indented = line.match(/^  (\w+):\s*"?([^"]*)"?$/);
      if (indented && currentObj) {
        currentObj[indented[1]] = indented[2];
        continue;
      }
      const top = line.match(/^(\w+):\s*(.*)$/);
      if (top) {
        const key = top[1];
        let val = top[2];
        if (val.startsWith('"') && val.endsWith('"')) val = val.slice(1, -1);
        if (val === '') {
          meta[key] = {};
          currentObj = meta[key];
        } else {
          meta[key] = val;
          currentObj = null;
        }
      }
    }

    for (const k in meta) {
      if (typeof meta[k] === 'object' && Object.keys(meta[k]).length === 0) {
        meta[k] = null;
      }
    }

    return { meta, body };
  }

  async function fetchJournalList() {
    try {
      const res = await fetch('/journals/index.json?t=' + Date.now());
      if (res.ok) {
        const data = await res.json();
        return data.files || [];
      }
    } catch (e) {
      console.warn('Could not fetch journal index:', e);
    }
    return [];
  }

  async function fetchArticle(filename) {
    const res = await fetch('/journals/' + filename + '?t=' + Date.now());
    if (!res.ok) throw new Error('Failed to fetch ' + filename);
    const text = await res.text();
    return parseArticle(text);
  }

  function formatYear(dateStr) {
    if (!dateStr) return '';
    return dateStr.substring(0, 4);
  }

  function renderTitle(title) {
    if (!title) return '';
    const escaped = title.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
    return escaped.replace(/\*([^*]+)\*/g, '<em>$1</em>');
  }

  function filenameToSlug(filename) {
    return filename
      .replace(/^\d{4}-\d{2}-\d{2}-/, '')
      .replace(/\.md$/, '');
  }

  async function renderJournalList() {
    const grid = document.querySelector('#page-journal .journal-grid');
    if (!grid) return;

    JOURNAL_FILES = await fetchJournalList();

    if (JOURNAL_FILES.length === 0) {
      grid.innerHTML = '<p style="color:var(--text-2);font-size:14px;">No articles yet.</p>';
      return;
    }

    const sorted = [...JOURNAL_FILES].sort((a, b) => b.localeCompare(a));

    const articles = await Promise.all(
      sorted.map(async (filename) => {
        try {
          const { meta } = await fetchArticle(filename);
          return { filename, meta };
        } catch (e) {
          console.error('Failed to load', filename, e);
          return null;
        }
      })
    );

    grid.innerHTML = articles
      .filter(Boolean)
      .map(({ filename, meta }) => {
        const slug = filenameToSlug(filename);
        const cover = meta.cover || '';
        const coverHtml = cover
          ? `<img src="${cover}" alt="${meta.title || ''}">`
          : '<div class="journal-cover-placeholder">Cover photo</div>';
        return `
          <div class="journal-card" onclick="openProject('journal-${slug}')">
            <div class="journal-cover">${coverHtml}</div>
            <div class="journal-card-text">
              <div class="journal-year">${formatYear(meta.date)}</div>
              <div class="journal-card-title">${renderTitle(meta.title)}</div>
              <div class="journal-card-excerpt">${meta.excerpt || ''}</div>
            </div>
          </div>
        `;
      })
      .join('');
  }

  async function renderArticle(slug) {
    if (JOURNAL_FILES.length === 0) {
      JOURNAL_FILES = await fetchJournalList();
    }

    const filename = JOURNAL_FILES.find(f => filenameToSlug(f) === slug);
    if (!filename) {
      console.error('Article not found:', slug);
      return false;
    }

    let pageId = 'page-journal-' + slug;
    let page = document.getElementById(pageId);

    if (!page) {
      page = document.createElement('div');
      page.className = 'page fade-in';
      page.id = pageId;
      document.body.appendChild(page);
    }

    try {
      const { meta, body } = await fetchArticle(filename);
      const heroHtml = meta.hero
        ? `<img src="${meta.hero}" alt="${meta.title || ''}">`
        : '<span class="journal-article-hero-placeholder">Hero photo</span>';

      const pp = meta.pair_photos || {};
      const hasPair = pp.left || pp.right;
      const pairHtml = hasPair ? `
        <div class="journal-article-pair">
          <div class="journal-article-pair-photo">
            ${pp.left ? `<img src="${pp.left}" alt="">` : '<span class="journal-article-pair-placeholder">Photo</span>'}
          </div>
          <div class="journal-article-pair-photo">
            ${pp.right ? `<img src="${pp.right}" alt="">` : '<span class="journal-article-pair-placeholder">Photo</span>'}
          </div>
        </div>
      ` : '';

      let bodyHtml = parseMarkdown(body);
      if (hasPair) {
        const olMatches = [...bodyHtml.matchAll(/<\/ol>/g)];
        if (olMatches.length >= 1) {
          const idx = olMatches[0].index + 5;
          bodyHtml = bodyHtml.slice(0, idx) + pairHtml + bodyHtml.slice(idx);
        } else {
          const parts = bodyHtml.split('</p>');
          const mid = Math.floor(parts.length / 2);
          bodyHtml = parts.slice(0, mid).join('</p>') + '</p>' + pairHtml + parts.slice(mid).join('</p>');
        }
      }

      page.innerHTML = `
        <div class="journal-article">
          <div class="journal-article-hero">${heroHtml}</div>
          <div class="journal-article-date">${formatYear(meta.date)}</div>
          <h1 class="journal-article-title">${renderTitle(meta.title)}</h1>
          <div class="journal-article-body">${bodyHtml}</div>
        </div>
      `;
      return true;
    } catch (e) {
      console.error('Failed to render article:', e);
      page.innerHTML = '<div class="journal-article"><p>Article not found.</p></div>';
      return false;
    }
  }

  window.JournalLoader = {
    renderList: renderJournalList,
    renderArticle: renderArticle
  };

  function maybeRenderForCurrentHash() {
    const hash = location.hash.replace('#', '');
    if (hash === 'journal') {
      renderJournalList();
    } else if (hash && hash.startsWith('journal-')) {
      const slug = hash.replace('journal-', '');
      renderArticle(slug);
    }
  }

  window.addEventListener('hashchange', maybeRenderForCurrentHash);
  window.addEventListener('load', () => {
    fetchJournalList().then(files => { JOURNAL_FILES = files; });
    maybeRenderForCurrentHash();
  });
})();

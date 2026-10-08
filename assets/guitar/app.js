'use strict';
(() => {
  const project = JSON.parse(document.getElementById('project-data').textContent);
  const byId = id => document.getElementById(id);
  const tasks = [...document.querySelectorAll('.task')];
  const fields = ['task-search', 'status-filter', 'phase-filter', 'priority-filter'];
  const filters = byId('task-filters');
  function filterTasks() {
    const query = byId('task-search').value.trim().toLocaleLowerCase();
    let visible = 0;
    for (const task of tasks) {
      const show = (!query || task.textContent.toLocaleLowerCase().includes(query)) &&
        [['status-filter','status'],['phase-filter','phase'],['priority-filter','priority']]
          .every(([id,key]) => byId(id).value === 'all' || byId(id).value === task.dataset[key]);
      task.hidden = !show;
      if (show) visible++;
    }
    byId('task-count').textContent = `显示 ${visible} / ${tasks.length} 项任务`;
    byId('empty-tasks').hidden = visible !== 0;
  }
  fields.forEach(id => byId(id).addEventListener(id === 'task-search' ? 'input' : 'change', filterTasks));
  filters.addEventListener('submit', event => event.preventDefault());
  filters.addEventListener('reset', () => requestAnimationFrame(filterTasks));
  function revealHashTarget() {
    const id = decodeURIComponent(location.hash.slice(1));
    if (!id.startsWith('task-')) return;
    const target = byId(id);
    if (!target || !target.classList.contains('task')) return;
    filters.reset();
    filterTasks();
    target.open = true;
    target.scrollIntoView({block:'start',behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
  }
  window.addEventListener('hashchange', revealHashTarget);
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#task-"]');
    if (link && link.hash === location.hash) revealHashTarget();
  });
  revealHashTarget();
  byId('clip-select').addEventListener('change', event => {
    const clip = project.clips.find(c => c.id === event.target.value);
    if (!clip) return;
    const video = byId('experiment-video');
    video.pause();
    video.src = clip.video;
    video.poster = clip.poster;
    video.setAttribute('aria-label', `${clip.name} 实际物理执行四视角视频`);
    video.load();
    byId('clip-title').textContent = `${clip.name} · ${clip.title}`;
    byId('clip-meta').textContent = `源帧 ${clip.sourceFrames.join('–')} · 源速度 ${clip.speed}×`;
    byId('clip-initialization').textContent = clip.initialization;
    byId('clip-download').href = clip.video;
    byId('clip-status').textContent = `历史版本 · ${clip.cases.filter(c=>c.passed).length}/4 通过`;
  });
  const navLinks = [...document.querySelectorAll('nav a')];
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      for (const entry of entries) if (entry.isIntersecting) {
        for (const link of navLinks) {
          const active = link.hash === '#' + entry.target.id;
          link.classList.toggle('active', active);
          if (active) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        }
      }
    }, {rootMargin:'-10% 0px -65% 0px', threshold:0});
    document.querySelectorAll('main > section[id]').forEach(section => observer.observe(section));
  }
})();

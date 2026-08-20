const announcer = document.querySelector('#action-announcer');

const legacyWorkspace = new URLSearchParams(window.location.search).get('workspace');
const legacyProjectId = new URLSearchParams(window.location.search).get('projectId') || 'the-last-dawn';
const legacyCharacterId = new URLSearchParams(window.location.search).get('characterId') || 'christopher';
const safeLegacySegment = (value, fallback) => /^[a-z0-9][a-z0-9_-]{0,127}$/i.test(value) ? value : fallback;
const legacyProject = safeLegacySegment(legacyProjectId, 'the-last-dawn');
const legacyCharacter = safeLegacySegment(legacyCharacterId, 'christopher');
const legacyWorkflowRoutes = {
  idea: `/studio/projects/${legacyProject}/idea`,
  discovery: `/discovery?projectId=${legacyProject}&characterId=${legacyCharacter}`,
  script: `/studio/projects/${legacyProject}/script`,
  'pre-production': `/studio/projects/${legacyProject}/pre-production/characters/${legacyCharacter}`,
  ready: `/studio/projects/${legacyProject}/ready`,
  set: `/studio/projects/${legacyProject}/set`,
  studio: `/studio/projects/${legacyProject}/studio`,
  render: `/studio/projects/${legacyProject}/render`,
  production: `/studio/projects/${legacyProject}/studio`,
};

if (legacyWorkspace && legacyWorkflowRoutes[legacyWorkspace]) {
  window.location.replace(legacyWorkflowRoutes[legacyWorkspace]);
}

const announce = (message) => {
  if (announcer) {
    announcer.textContent = message;
  }
};

const isTextEntryTarget = (target) => Boolean(target?.closest?.('input, textarea, select, [contenteditable="true"]'));

const workspaceStorageKey = 'nexkosmo.studioWorkspace';

const readWorkspacePreferences = () => {
  try {
    return JSON.parse(window.localStorage.getItem(workspaceStorageKey) || '{}');
  } catch {
    return {};
  }
};

const writeWorkspacePreferences = (changes) => {
  try {
    window.localStorage.setItem(workspaceStorageKey, JSON.stringify({
      ...readWorkspacePreferences(),
      ...changes,
    }));
  } catch {
    // Workspace controls remain functional when storage is unavailable.
  }
};

const initEcosystemTabs = () => {
  const tabs = [...document.querySelectorAll('.ecosystem-tabs [role="tab"]')];
  const navigationLinks = [...document.querySelectorAll('.primary-nav [data-ecosystem-target]')];
  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  let targetConfirmationTimer;

  const activateTab = (activeTab) => {
    tabs.forEach((tab) => {
      const selected = tab === activeTab;
      tab.setAttribute('aria-selected', String(selected));
      tab.tabIndex = selected ? 0 : -1;
    });

    navigationLinks.forEach((link) => {
      if (link.dataset.ecosystemTarget === activeTab.dataset.tab) {
        link.setAttribute('aria-current', 'page');
      } else {
        link.removeAttribute('aria-current');
      }
    });

    announce(`${activeTab.dataset.tab} selected.`);
  };

  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activateTab(tab));
    tab.addEventListener('keydown', (event) => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) {
        return;
      }

      event.preventDefault();
      const lastIndex = tabs.length - 1;
      let nextIndex = index;

      if (event.key === 'Home') nextIndex = 0;
      if (event.key === 'End') nextIndex = lastIndex;
      if (event.key === 'ArrowRight') nextIndex = index === lastIndex ? 0 : index + 1;
      if (event.key === 'ArrowLeft') nextIndex = index === 0 ? lastIndex : index - 1;

      tabs[nextIndex].focus();
      activateTab(tabs[nextIndex]);
    });
  });

  navigationLinks.forEach((link) => {
    link.addEventListener('click', (event) => {
      const matchingTab = tabs.find((tab) => tab.dataset.tab === link.dataset.ecosystemTarget);
      const anchorTarget = document.querySelector(link.hash);

      if (!matchingTab || !anchorTarget) return;

      event.preventDefault();
      activateTab(matchingTab);
      window.history.replaceState(null, '', link.hash);

      anchorTarget.scrollIntoView({
        behavior: reducedMotion ? 'auto' : 'smooth',
        block: link.hash === '#create' ? 'start' : 'center',
      });

      const confirmationTarget = link.hash === '#create'
        ? document.querySelector('#ai-producer')
        : anchorTarget;

      if (confirmationTarget) {
        window.clearTimeout(targetConfirmationTimer);
        document.querySelector('.is-nav-target')?.classList.remove('is-nav-target');
        confirmationTarget.classList.remove('is-nav-target');
        void confirmationTarget.offsetWidth;
        confirmationTarget.classList.add('is-nav-target');
        targetConfirmationTimer = window.setTimeout(() => {
          confirmationTarget.classList.remove('is-nav-target');
        }, 1600);
      }
    });
  });
};

const initAssetTurntables = () => {
  const turntables = [...document.querySelectorAll('[data-asset-turntable]')];

  turntables.forEach((turntable) => {
    let rotation = 0;
    let pointerId = null;
    let pointerStartX = 0;
    let rotationAtPointerStart = 0;
    let dragged = false;

    turntable.title = 'Drag or use the left and right arrow keys to rotate';

    const renderRotation = () => {
      const normalizedRotation = ((Math.round(rotation) % 360) + 360) % 360;
      let viewDescription = `${normalizedRotation} degree view`;

      if (normalizedRotation === 0) viewDescription = 'Front view';
      if (normalizedRotation >= 170 && normalizedRotation <= 190) viewDescription = 'Rear view';

      turntable.style.setProperty('--asset-rotation', `${rotation}deg`);
      turntable.setAttribute('aria-valuenow', String(normalizedRotation));
      turntable.setAttribute('aria-valuetext', viewDescription);
    };

    const finishPointerRotation = (event) => {
      if (pointerId !== event.pointerId) return;

      turntable.releasePointerCapture?.(pointerId);
      turntable.classList.remove('is-turning');
      pointerId = null;

      if (dragged) {
        announce(`${turntable.getAttribute('aria-label')} set to ${turntable.getAttribute('aria-valuetext')}.`);
      }
    };

    turntable.addEventListener('pointerdown', (event) => {
      if (event.button !== 0) return;

      event.preventDefault();
      event.stopPropagation();
      pointerId = event.pointerId;
      pointerStartX = event.clientX;
      rotationAtPointerStart = rotation;
      dragged = false;
      turntable.classList.add('is-turning');
      turntable.setPointerCapture?.(pointerId);
      turntable.focus({ preventScroll: true });
    });

    turntable.addEventListener('pointermove', (event) => {
      if (pointerId !== event.pointerId) return;

      const pointerDistance = event.clientX - pointerStartX;
      dragged = dragged || Math.abs(pointerDistance) > 3;
      rotation = rotationAtPointerStart + pointerDistance * .9;
      renderRotation();
    });

    turntable.addEventListener('pointerup', finishPointerRotation);
    turntable.addEventListener('pointercancel', finishPointerRotation);
    turntable.addEventListener('click', (event) => {
      event.preventDefault();
      event.stopPropagation();
    });

    turntable.addEventListener('keydown', (event) => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;

      event.preventDefault();
      event.stopPropagation();

      if (event.key === 'ArrowLeft') rotation -= 15;
      if (event.key === 'ArrowRight') rotation += 15;
      if (event.key === 'Home') rotation = 0;
      if (event.key === 'End') rotation = 180;

      renderRotation();
      announce(`${turntable.getAttribute('aria-label')} set to ${turntable.getAttribute('aria-valuetext')}.`);
    });

    renderRotation();
  });
};

const initAiProducer = () => {
  const suggestions = [...document.querySelectorAll('[data-ai-suggestion]')];

  suggestions.forEach((button) => {
    button.setAttribute('aria-pressed', 'false');
    button.addEventListener('click', () => {
      const applied = button.getAttribute('aria-pressed') === 'true';
      button.setAttribute('aria-pressed', String(!applied));
      button.querySelector('strong').textContent = applied ? 'Apply' : 'Applied';
      announce(`${button.dataset.aiSuggestion} ${applied ? 'removed' : 'applied'}.`);
    });
  });
};

const initPlayback = () => {
  const playbackControls = [...document.querySelectorAll('[data-play-toggle]')];
  let playing = false;

  const renderPlaybackState = () => {
    playbackControls.forEach((button) => {
      button.textContent = playing ? 'Ⅱ' : '▶';
      button.setAttribute('aria-label', playing ? 'Pause Eclipse scene' : 'Play Eclipse scene');
      button.setAttribute('aria-pressed', String(playing));
    });
  };

  playbackControls.forEach((button) => {
    button.addEventListener('click', () => {
      playing = !playing;
      renderPlaybackState();
      announce(playing ? 'Eclipse scene playing.' : 'Eclipse scene paused.');
    });
  });

  renderPlaybackState();
};

const initHeaderUtilities = () => {
  const triggers = [...document.querySelectorAll('[data-header-panel]')];
  const panels = [...document.querySelectorAll('[data-header-popover]')];

  if (!triggers.length || !panels.length) return;

  let activeTrigger = null;

  const closeAll = (returnFocus = false) => {
    panels.forEach((panel) => { panel.hidden = true; });
    triggers.forEach((trigger) => trigger.setAttribute('aria-expanded', 'false'));

    if (returnFocus && activeTrigger) activeTrigger.focus();
    activeTrigger = null;
  };

  const openPanel = (trigger) => {
    const panel = document.getElementById(trigger.dataset.headerPanel);

    if (!panel) return;

    const wasOpen = trigger.getAttribute('aria-expanded') === 'true';
    closeAll();

    if (wasOpen) return;

    panel.hidden = false;
    trigger.setAttribute('aria-expanded', 'true');
    activeTrigger = trigger;

    const focusTarget = panel.querySelector('input, h2[tabindex="-1"]');
    window.setTimeout(() => focusTarget?.focus(), 0);
    announce(`${trigger.getAttribute('aria-label')} opened.`);
  };

  triggers.forEach((trigger) => {
    trigger.addEventListener('click', (event) => {
      event.stopPropagation();
      openPanel(trigger);
    });
  });

  panels.forEach((panel) => {
    panel.querySelector('[data-popover-close]')?.addEventListener('click', () => closeAll(true));
    panel.querySelectorAll('[data-popover-navigate]').forEach((link) => {
      link.addEventListener('click', () => closeAll());
    });
  });

  document.addEventListener('pointerdown', (event) => {
    if (!event.target.closest('[data-header-popover], [data-header-panel]')) closeAll();
  });

  document.addEventListener('keydown', (event) => {
    if (event.key === 'Escape' && activeTrigger) closeAll(true);
  });

  window.addEventListener('nexkosmo:open-header-panel', (event) => {
    const trigger = triggers.find((item) => item.dataset.headerPanel === event.detail?.id);
    if (trigger) openPanel(trigger);
  });

  const searchForm = document.querySelector('[data-header-search]');
  const searchStatus = document.querySelector('[data-search-status]');
  const searchCatalog = ['AI Producer', 'Eclipse', 'Movies & Series', 'Marketplace', 'Achieve Rewards', 'Ethan Rewards', 'Heidi Leaderboards', 'Membership Plans', 'Cinematic City Pack', 'Dragon Creature', 'Epic Sword', 'VFX Explosion Pack', 'Ambient Music Loop', 'Cyber Soldier'];

  searchForm?.addEventListener('submit', (event) => {
    event.preventDefault();
    const query = new FormData(searchForm).get('query')?.toString().trim() || '';
    const matches = searchCatalog.filter((item) => item.toLowerCase().includes(query.toLowerCase()));
    const message = !query
      ? 'Enter a creator, project, or asset name.'
      : matches.length
        ? `Matches: ${matches.join(', ')}.`
        : `No current matches for “${query}”.`;

    if (searchStatus) searchStatus.textContent = message;
    announce(message);
  });

  document.querySelector('[data-mark-notifications]')?.addEventListener('click', () => {
    const badge = document.querySelector('[data-header-panel="header-notifications"] .icon-button__badge');
    const status = document.querySelector('[data-notification-status]');

    if (badge) badge.hidden = true;
    if (status) status.textContent = 'All notifications marked as read.';
    announce('All notifications marked as read.');
  });

  document.querySelector('[data-open-inbox]')?.addEventListener('click', () => {
    const badge = document.querySelector('[data-header-panel="header-mail"] .icon-button__badge');
    const status = document.querySelector('[data-mail-status]');

    if (badge) badge.hidden = true;
    if (status) status.textContent = 'Inbox preview opened. Account messaging can be connected here.';
    announce('Inbox preview opened.');
  });
};

const initCreatorPulse = () => {
  const storageKey = 'nexkosmo.creatorPulse';
  const scopeControl = document.querySelector('[data-creator-pulse-scope]');
  const settingStatus = document.querySelector('[data-creator-pulse-setting-status]');
  const previewControl = document.querySelector('[data-creator-pulse-preview]');
  const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  const previewMode = new URLSearchParams(window.location.search).get('pulse') === 'preview';
  const queue = [];
  const queueLimit = 8;
  const displayDuration = 4600;
  let current = null;
  let component = null;
  let dismissTimer = 0;
  let queueTimer = 0;
  let ambientTimer = 0;
  let previewIndex = 0;

  const randomInterval = () => 120000 + Math.floor(Math.random() * 60001);
  let nextEligibleAt = Date.now() + randomInterval();

  const eventTypes = Object.freeze({
    reward: { icon: '🎁', title: 'Ethan Rewards™', href: '#earn', priority: 90, category: 'rewards' },
    leaderboard: { icon: '🏆', title: 'Heidi Leaderboards™', href: '#community', priority: 85, category: 'rewards' },
    film: { icon: '🎬', title: 'New Film Published', href: '#studio', priority: 60, category: 'activity' },
    sale: { icon: '🛒', title: 'Marketplace Sale', href: '#marketplace', priority: 55, category: 'marketplace' },
    legend: { icon: '👑', title: 'Hall of Legends', href: '#community', priority: 80, category: 'activity' },
    milestone: { icon: '⭐', title: 'Creator Milestone', href: '#community', priority: 70, category: 'activity' },
  });

  const sampleEvents = [
    { type: 'reward', creator: 'Sarah', initials: 'SA', message: 'unlocked Cyber Soldier Pack', audiences: ['all', 'friends', 'following', 'rewards'], region: true },
    { type: 'leaderboard', creator: 'Michael', initials: 'MI', message: 'reached Gold Creator', audiences: ['all', 'following', 'rewards'], region: false },
    { type: 'film', creator: 'Amara', initials: 'AM', message: 'published The Last Horizon', audiences: ['all', 'friends', 'following'], region: true },
    { type: 'sale', creator: 'Jules', initials: 'JU', message: 'sold the Neon District environment', audiences: ['all', 'marketplace'], region: false },
    { type: 'legend', creator: 'Nia', initials: 'NI', message: 'entered the Hall of Legends', audiences: ['all', 'following'], region: true },
    { type: 'milestone', creator: 'Kenji', initials: 'KE', message: 'completed 100 cinematic scenes', audiences: ['all', 'friends', 'following'], region: false },
  ];

  const readPreference = () => {
    try {
      return window.localStorage.getItem(storageKey) || 'all';
    } catch {
      return 'all';
    }
  };

  const writePreference = (scope) => {
    try {
      window.localStorage.setItem(storageKey, scope);
    } catch {
      // Creator Pulse remains usable if storage is unavailable.
    }
  };

  const isPaused = () => {
    const shell = document.querySelector('.studio-shell');
    const root = document.documentElement;
    return document.hidden
      || Boolean(document.fullscreenElement)
      || root.dataset.presentationMode === 'true'
      || root.dataset.exporting === 'true'
      || root.dataset.userSettingsOpen === 'true'
      || shell?.dataset.rendering === 'true'
      || shell?.getAttribute('aria-busy') === 'true';
  };

  const normalizeEvent = (source) => {
    const definition = eventTypes[source?.type];
    if (!definition || !source?.message) return null;
    const creator = source.creator || 'A Nexkosmo creator';
    return {
      ...definition,
      ...source,
      creator,
      initials: source.initials || creator.split(/\s+/).map((part) => part[0]).join('').slice(0, 2).toUpperCase(),
      priority: Number.isFinite(source.priority) ? source.priority : definition.priority,
      timestamp: source.timestamp || 'Just now',
    };
  };

  const passesPreference = (event) => {
    const preference = readPreference();
    if (preference === 'off') return false;
    if (preference === 'all') return true;
    if (preference === 'region') return event.region === true;
    if (preference === 'marketplace') return event.category === 'marketplace';
    if (preference === 'rewards') return event.category === 'rewards';
    return event.audiences?.includes(preference) === true;
  };

  const createComponent = () => {
    if (component) return component;
    const host = document.createElement('aside');
    host.className = 'creator-pulse-host';
    host.setAttribute('aria-label', 'Creator Pulse activity');
    host.setAttribute('aria-live', 'polite');
    host.setAttribute('aria-atomic', 'true');
    host.innerHTML = `
      <a class="creator-pulse" href="#community" hidden>
        <span class="creator-pulse__avatar" aria-hidden="true"></span>
        <span class="creator-pulse__copy">
          <strong class="creator-pulse__title"><i aria-hidden="true"></i><b></b></strong>
          <span class="creator-pulse__message"></span>
          <time class="creator-pulse__time"></time>
        </span>
        <span class="creator-pulse__celebration" aria-hidden="true">${'<i></i>'.repeat(8)}</span>
      </a>`;
    document.body.append(host);
    const toast = host.querySelector('.creator-pulse');
    component = {
      toast,
      avatar: host.querySelector('.creator-pulse__avatar'),
      icon: host.querySelector('.creator-pulse__title i'),
      title: host.querySelector('.creator-pulse__title b'),
      message: host.querySelector('.creator-pulse__message'),
      time: host.querySelector('.creator-pulse__time'),
    };
    return component;
  };

  const scheduleQueue = (delay) => {
    window.clearTimeout(queueTimer);
    queueTimer = window.setTimeout(showNext, Math.max(0, delay));
  };

  const dismissCurrent = () => {
    if (!current || !component) return;
    window.clearTimeout(dismissTimer);
    component.toast.classList.add('creator-pulse--leaving');
    const finishDelay = reducedMotionQuery.matches ? 20 : 340;
    window.setTimeout(() => {
      component.toast.hidden = true;
      component.toast.classList.remove('creator-pulse--visible', 'creator-pulse--leaving', 'creator-pulse--self');
      current = null;
      scheduleQueue(500);
    }, finishDelay);
  };

  function showNext() {
    window.clearTimeout(queueTimer);
    if (current || !queue.length || isPaused()) return;
    const bypassIndex = queue.findIndex((item) => item.bypassFrequency);
    const now = Date.now();
    if (bypassIndex < 0 && now < nextEligibleAt) {
      scheduleQueue(nextEligibleAt - now);
      return;
    }
    const entry = queue.splice(bypassIndex >= 0 ? bypassIndex : 0, 1)[0];
    const event = entry.event;
    const view = createComponent();
    const isRichSelfAchievement = event.isSelf === true && ['reward', 'leaderboard'].includes(event.type);
    current = entry;
    view.avatar.textContent = event.initials;
    if (event.avatarUrl) {
      const avatarImage = document.createElement('img');
      avatarImage.src = event.avatarUrl;
      avatarImage.alt = '';
      avatarImage.loading = 'lazy';
      avatarImage.decoding = 'async';
      view.avatar.replaceChildren(avatarImage);
    }
    view.icon.textContent = event.icon;
    view.title.textContent = event.title;
    view.message.textContent = `${event.creator} ${event.message}`;
    view.time.textContent = event.timestamp;
    view.toast.href = event.href;
    view.toast.setAttribute('aria-label', `${event.title}. ${event.creator} ${event.message}. ${event.timestamp}. Open related page.`);
    view.toast.classList.toggle('creator-pulse--self', isRichSelfAchievement);
    view.toast.hidden = false;
    view.toast.classList.remove('creator-pulse--leaving');
    requestAnimationFrame(() => view.toast.classList.add('creator-pulse--visible'));
    announce(`${event.title}. ${event.creator} ${event.message}.`);
    if (!entry.bypassFrequency) nextEligibleAt = now + randomInterval();
    dismissTimer = window.setTimeout(dismissCurrent, displayDuration);
  }

  const publish = (source, options = {}) => {
    const event = normalizeEvent(source);
    if (!event || !passesPreference(event)) return false;
    const entry = { event, bypassFrequency: options.bypassFrequency === true };
    if (queue.length >= queueLimit) {
      const lowestIndex = queue.reduce((lowest, item, index, items) => (
        item.event.priority < items[lowest].event.priority ? index : lowest
      ), 0);
      if (queue[lowestIndex].event.priority >= event.priority) return false;
      queue.splice(lowestIndex, 1);
    }
    queue.push(entry);
    queue.sort((a, b) => b.event.priority - a.event.priority);
    showNext();
    return true;
  };

  const scheduleAmbientEvent = () => {
    window.clearTimeout(ambientTimer);
    ambientTimer = window.setTimeout(() => {
      const sample = sampleEvents[Math.floor(Math.random() * sampleEvents.length)];
      publish(sample);
      scheduleAmbientEvent();
    }, randomInterval());
  };

  scopeControl?.addEventListener('change', () => {
    writePreference(scopeControl.value);
    queue.length = 0;
    if (scopeControl.value === 'off') dismissCurrent();
    const selectedLabel = scopeControl.options[scopeControl.selectedIndex]?.text || 'All Activity';
    if (settingStatus) settingStatus.textContent = scopeControl.value === 'off'
      ? 'Creator Pulse™ is off.'
      : `${selectedLabel} will appear quietly while you work.`;
    announce(`Creator Pulse set to ${selectedLabel}.`);
  });

  previewControl?.addEventListener('click', () => {
    const standard = sampleEvents[previewIndex % sampleEvents.length];
    const selfReward = { type: 'reward', creator: 'You', initials: 'CT', message: 'earned the Eclipse Pioneer reward', isSelf: true, audiences: ['all', 'friends', 'following', 'rewards'], region: true };
    const sample = previewIndex % 2 === 0 ? selfReward : standard;
    previewIndex += 1;
    if (readPreference() === 'off') {
      if (settingStatus) settingStatus.textContent = 'Turn Creator Pulse™ on to preview it.';
      return;
    }
    publish(sample, { bypassFrequency: true });
    if (settingStatus) settingStatus.textContent = 'Preview sent. The next preview alternates between personal and community activity.';
  });

  window.addEventListener('nexkosmo:creator-pulse', (event) => publish(event.detail));
  window.addEventListener('nexkosmo:studio-state', showNext);
  document.addEventListener('visibilitychange', showNext);
  document.addEventListener('fullscreenchange', showNext);
  if (scopeControl) scopeControl.value = readPreference();
  scheduleAmbientEvent();
  window.NexkosmoCreatorPulse = Object.freeze({ publish, types: Object.freeze(Object.keys(eventTypes)) });

  if (previewMode && readPreference() !== 'off') {
    window.setTimeout(() => publish({
      type: 'reward', creator: 'You', initials: 'CT', message: 'earned the Eclipse Pioneer reward', isSelf: true,
      audiences: ['all', 'friends', 'following', 'rewards'], region: true,
    }, { bypassFrequency: true }), 1200);
  }
};

const initCollaborationHub = () => {
  const hub = document.querySelector('#header-collaboration');
  if (!hub) return;

  const tabs = [...hub.querySelectorAll('[data-collab-tab]')];
  const panels = [...hub.querySelectorAll('[data-collab-panel]')];
  const searchForm = hub.querySelector('[data-collab-search]');
  const searchInput = searchForm?.querySelector('[name="query"]');
  const searchField = searchForm?.querySelector('[name="field"]');
  const searchSummary = hub.querySelector('[data-creator-search-summary]');
  const creatorCards = [...hub.querySelectorAll('[data-creator-card]')];
  const inviteForm = hub.querySelector('[data-collab-invite-form]');
  const inviteMethod = hub.querySelector('[data-invite-method]');
  const recipientGroup = hub.querySelector('[data-invite-recipient]');
  const recipientInput = recipientGroup?.querySelector('input');
  const recipientLabel = recipientGroup?.querySelector('label');
  const roleControl = hub.querySelector('[data-collab-role]');
  const shareLink = hub.querySelector('[data-collab-share-link]');
  const qrPanel = hub.querySelector('#collaboration-qr');
  const qrToggle = hub.querySelector('[data-toggle-collab-qr]');
  const status = hub.querySelector('[data-collab-status]');
  const directConversation = document.querySelector('[data-direct-conversation]');
  const storageKey = 'nexkosmo.collaborationHub';

  const roles = Object.freeze({
    owner: { label: 'Owner', capabilities: ['all', 'billing', 'delete'] },
    admin: { label: 'Admin', capabilities: ['manage-team', 'manage-project', 'publish'] },
    director: { label: 'Director', capabilities: ['manage-scenes', 'approve', 'publish'] },
    producer: { label: 'Producer', capabilities: ['manage-project', 'invite', 'approve'] },
    writer: { label: 'Writer', capabilities: ['edit-script', 'comment'] },
    artist: { label: 'Artist', capabilities: ['edit-assets', 'comment'] },
    animator: { label: 'Animator', capabilities: ['edit-animation', 'comment'] },
    composer: { label: 'Composer', capabilities: ['edit-audio', 'comment'] },
    developer: { label: 'Developer', capabilities: ['edit-tools', 'integrate', 'comment'] },
    reviewer: { label: 'Reviewer', capabilities: ['review', 'comment'] },
    viewer: { label: 'Viewer', capabilities: ['view'] },
  });

  const futureCapabilities = Object.freeze([
    'live-collaboration', 'voice-calls', 'video-meetings', 'screen-sharing',
    'shared-editing', 'presence', 'ai-meeting-summaries', 'studio-organisations', 'enterprise-teams',
  ]);

  const notificationTypes = Object.freeze({
    invitationReceived: 'Collaboration invitation received',
    invitationAccepted: 'Collaboration invitation accepted',
    userJoined: 'Creator joined project',
    userLeft: 'Creator left project',
    sharedProject: 'New shared project',
    permissionChanged: 'Collaboration permission changed',
    invitationSent: 'Collaboration invitation sent',
  });

  const readState = () => {
    try {
      return JSON.parse(window.localStorage.getItem(storageKey) || '{"following":[]}');
    } catch {
      return { following: [] };
    }
  };

  const writeState = (nextState) => {
    try {
      window.localStorage.setItem(storageKey, JSON.stringify(nextState));
    } catch {
      // Collaboration remains functional when storage is unavailable.
    }
  };

  const setStatus = (message) => {
    if (status) status.textContent = message;
    announce(message);
  };

  const notify = (type, detail = {}) => {
    const title = notificationTypes[type];
    if (!title) return false;
    const feed = document.querySelector('#header-notifications .header-feed');
    const badge = document.querySelector('[data-header-panel="header-notifications"] .icon-button__badge');
    if (!feed) return false;
    const item = document.createElement('li');
    const signal = document.createElement('i');
    const copy = document.createElement('span');
    const heading = document.createElement('strong');
    const message = document.createElement('small');
    const timestamp = document.createElement('time');
    signal.className = type === 'userLeft' ? 'header-feed__signal header-feed__signal--amber' : 'header-feed__signal header-feed__signal--green';
    signal.setAttribute('aria-hidden', 'true');
    heading.textContent = title;
    message.textContent = detail.message || `${detail.creator || 'A creator'} · ${detail.project || 'Eclipse'}`;
    timestamp.textContent = 'Now';
    copy.append(heading, message);
    item.append(signal, copy, timestamp);
    feed.prepend(item);
    while (feed.children.length > 6) feed.lastElementChild?.remove();
    if (badge) {
      badge.hidden = false;
      badge.textContent = String(Math.min(9, (Number.parseInt(badge.textContent || '0', 10) || 0) + 1));
    }
    return true;
  };

  const activateTab = (tab, moveFocus = false) => {
    const target = tab.dataset.collabTab;
    tabs.forEach((item) => {
      const selected = item === tab;
      item.setAttribute('aria-selected', String(selected));
      item.tabIndex = selected ? 0 : -1;
    });
    panels.forEach((panel) => { panel.hidden = panel.dataset.collabPanel !== target; });
    if (moveFocus) tab.focus();
  };

  tabs.forEach((tab, index) => {
    tab.addEventListener('click', () => activateTab(tab));
    tab.addEventListener('keydown', (event) => {
      if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
      event.preventDefault();
      let nextIndex = index;
      if (event.key === 'Home') nextIndex = 0;
      if (event.key === 'End') nextIndex = tabs.length - 1;
      if (event.key === 'ArrowRight') nextIndex = (index + 1) % tabs.length;
      if (event.key === 'ArrowLeft') nextIndex = (index - 1 + tabs.length) % tabs.length;
      activateTab(tabs[nextIndex], true);
    });
  });

  const renderSearch = () => {
    const query = searchInput?.value.trim().toLowerCase() || '';
    const field = searchField?.value || 'all';
    let matches = 0;
    creatorCards.forEach((card) => {
      const haystack = field === 'all'
        ? ['username', 'name', 'skills', 'country', 'language', 'studio'].map((key) => card.dataset[key] || '').join(' ')
        : card.dataset[field] || '';
      const matched = !query || haystack.toLowerCase().includes(query);
      card.hidden = !matched;
      if (matched) matches += 1;
    });
    if (searchSummary) searchSummary.textContent = query
      ? `${matches} creator${matches === 1 ? '' : 's'} found for “${searchInput.value.trim()}”`
      : `${matches} recommended creators`;
  };

  searchForm?.addEventListener('submit', (event) => { event.preventDefault(); renderSearch(); });
  searchInput?.addEventListener('input', renderSearch);
  searchField?.addEventListener('change', renderSearch);

  const following = new Set(readState().following || []);
  hub.querySelectorAll('[data-collab-follow]').forEach((button) => {
    const isFollowing = following.has(button.dataset.collabFollow);
    button.setAttribute('aria-pressed', String(isFollowing));
    if (isFollowing) button.textContent = 'Following';
  });

  hub.addEventListener('click', (event) => {
    const profileButton = event.target.closest('[data-collab-profile]');
    const messageButton = event.target.closest('[data-collab-message]');
    const inviteButton = event.target.closest('[data-collab-invite]');
    const followButton = event.target.closest('[data-collab-follow]');
    if (profileButton) {
      if (searchSummary) searchSummary.textContent = `${profileButton.dataset.collabProfile}'s creator profile is ready to open.`;
      announce(`${profileButton.dataset.collabProfile} profile selected.`);
    }
    if (messageButton) {
      if (directConversation) {
        directConversation.hidden = false;
        directConversation.querySelector('.header-feed__avatar').textContent = messageButton.dataset.collabInitials || 'NC';
        directConversation.querySelector('strong').textContent = messageButton.dataset.collabMessage;
      }
      window.dispatchEvent(new CustomEvent('nexkosmo:open-header-panel', { detail: { id: 'header-mail' } }));
      const mailStatus = document.querySelector('[data-mail-status]');
      if (mailStatus) mailStatus.textContent = `Direct conversation with ${messageButton.dataset.collabMessage} is ready in Mail.`;
      announce(`Direct conversation with ${messageButton.dataset.collabMessage} opened in Mail.`);
    }
    if (inviteButton) {
      const card = inviteButton.closest('[data-creator-card]');
      const inviteTab = tabs.find((tab) => tab.dataset.collabTab === 'invite');
      if (inviteTab) activateTab(inviteTab);
      if (inviteMethod) inviteMethod.value = 'username';
      if (recipientInput) recipientInput.value = card?.dataset.username || inviteButton.dataset.collabInvite;
      syncInviteMethod();
      setStatus(`${inviteButton.dataset.collabInvite} is ready to invite to Eclipse.`);
    }
    if (followButton) {
      const name = followButton.dataset.collabFollow;
      const active = followButton.getAttribute('aria-pressed') === 'true';
      followButton.setAttribute('aria-pressed', String(!active));
      followButton.textContent = active ? 'Follow Creator' : 'Following';
      if (active) following.delete(name); else following.add(name);
      writeState({ ...readState(), following: [...following] });
      announce(`${active ? 'Unfollowed' : 'Following'} ${name}.`);
    }
  });

  Object.entries(roles).forEach(([value, role]) => {
    const option = document.createElement('option');
    option.value = value;
    option.textContent = role.label;
    if (value === 'artist') option.selected = true;
    roleControl?.append(option);
  });

  function syncInviteMethod() {
    const method = inviteMethod?.value || 'username';
    const needsRecipient = ['username', 'email'].includes(method);
    if (recipientGroup) recipientGroup.hidden = !needsRecipient;
    if (recipientInput) {
      recipientInput.required = needsRecipient;
      recipientInput.type = method === 'email' ? 'email' : 'text';
      recipientInput.placeholder = method === 'email' ? 'creator@example.com' : '@creator';
    }
    if (recipientLabel) recipientLabel.textContent = method === 'email' ? 'Email address' : 'Creator username';
    if (method === 'share') setStatus('Copy the secure project link and send it through your preferred channel.');
    if (method === 'qr') {
      if (qrPanel) qrPanel.hidden = false;
      qrToggle?.setAttribute('aria-expanded', 'true');
      setStatus('The project QR invitation is ready to share.');
    }
  }

  inviteMethod?.addEventListener('change', syncInviteMethod);

  inviteForm?.addEventListener('submit', (event) => {
    event.preventDefault();
    const formData = new FormData(inviteForm);
    const method = formData.get('method');
    const recipient = ['share', 'qr'].includes(method) ? (method === 'share' ? 'share-link recipient' : 'QR recipient') : formData.get('recipient')?.toString().trim();
    if (!recipient) {
      setStatus('Enter a username or email address before sending the invitation.');
      recipientInput?.focus();
      return;
    }
    const role = roles[formData.get('role')]?.label || 'Collaborator';
    const project = formData.get('project')?.toString() || 'Eclipse';
    const accountMessage = method === 'email' ? ' If they are new to Nexkosmo, the project connection will complete after registration.' : '';
    setStatus(`Invitation prepared for ${recipient} as ${role} on ${project}.${accountMessage}`);
    notify('invitationSent', { creator: recipient, project, message: `${recipient} invited as ${role} · ${project}` });
  });

  hub.querySelector('[data-copy-collab-link]')?.addEventListener('click', async () => {
    try {
      await navigator.clipboard.writeText(shareLink?.value || '');
      setStatus('Secure collaboration link copied.');
    } catch {
      shareLink?.select();
      setStatus('Collaboration link selected. Copy it with your keyboard or device controls.');
    }
  });

  qrToggle?.addEventListener('click', () => {
    if (!qrPanel) return;
    const expanded = qrToggle.getAttribute('aria-expanded') === 'true';
    qrToggle.setAttribute('aria-expanded', String(!expanded));
    qrPanel.hidden = expanded;
    setStatus(expanded ? 'QR invitation hidden.' : 'Project QR invitation ready.');
  });

  window.addEventListener('nexkosmo:collaboration-event', (event) => notify(event.detail?.type, event.detail));
  window.NexkosmoCollaboration = Object.freeze({
    roles,
    notificationTypes,
    futureCapabilities,
    notify,
  });
  renderSearch();
  syncInviteMethod();
};

const initActionAnnouncements = () => {
  document.querySelectorAll('[data-action]').forEach((control) => {
    control.addEventListener('click', () => announce(`${control.dataset.action}.`));
  });
};

const initVisibilityAwareness = () => {
  const stage = document.querySelector('.cinematic-os');

  document.addEventListener('visibilitychange', () => {
    stage?.classList.toggle('is-paused', document.hidden);
  });
};

const initTerminalMotion = () => {
  const stage = document.querySelector('.cinematic-os');
  const labels = [...document.querySelectorAll('[data-terminal-refresh]')];

  if (!stage || !labels.length) return;

  const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
  const previewRequested = new URLSearchParams(window.location.search).get('motion') === 'preview';
  const motionEnabled = previewRequested || !reducedMotion.matches;
  const glyphs = '0123456789ABCDEF:.-';
  const baseIntervals = [13700, 16900, 19300, 22700];

  document.documentElement.dataset.motionPreview = String(previewRequested);
  stage.dataset.terminalMotionAttached = 'true';
  stage.dataset.terminalMotionMode = motionEnabled ? 'active' : 'reduced';

  if (!motionEnabled) return;

  const scrambleTo = (label, nextText) => {
    const currentText = label.textContent.trim();

    if (!nextText || currentText === nextText) return;

    const frameCount = 8;
    let frame = 0;

    label.classList.add('is-terminal-refreshing');
    label.setAttribute('aria-busy', 'true');
    label.setAttribute('aria-label', nextText);

    const refresh = window.setInterval(() => {
      frame += 1;
      const revealTo = Math.floor((frame / frameCount) * nextText.length);

      label.textContent = [...nextText].map((character, index) => {
        if (character === ' ' || index < revealTo) return character;
        return glyphs[Math.floor(Math.random() * glyphs.length)];
      }).join('');

      if (frame >= frameCount) {
        window.clearInterval(refresh);
        label.textContent = nextText;
        label.classList.remove('is-terminal-refreshing');
        label.setAttribute('aria-busy', 'false');
      }
    }, 68);
  };

  labels.forEach((label, labelIndex) => {
    const values = (label.dataset.terminalValues || '')
      .split('|')
      .map((value) => value.trim())
      .filter(Boolean);

    if (values.length < 2) return;

    let valueIndex = Math.max(0, values.indexOf(label.textContent.trim()));
    let cycle = 0;

    const scheduleRefresh = (delay) => {
      window.setTimeout(() => {
        if (!document.hidden) {
          valueIndex = (valueIndex + 1) % values.length;
          scrambleTo(label, values[valueIndex]);
          cycle += 1;
        }

        const irregularOffset = (cycle * 2713 + labelIndex * 947) % 4300;
        scheduleRefresh(baseIntervals[labelIndex % baseIntervals.length] + irregularOffset);
      }, delay);
    };

    scheduleRefresh(5200 + labelIndex * 1700);
  });
};

const initStudioNavigation = () => {
  const shell = document.querySelector('.studio-shell');
  const navigation = document.querySelector('#studio-navigation');
  const toggle = document.querySelector('[data-studio-nav-toggle]');
  const drawerOpenButton = document.querySelector('[data-studio-drawer-open]');
  const drawerCloseButton = document.querySelector('[data-studio-drawer-close]');
  const items = [...document.querySelectorAll('[data-studio-nav-item]')];

  if (!shell || !navigation || !toggle || !drawerOpenButton || !items.length) return;

  const storageKey = 'nexkosmo.studioSidebar';
  const mobileQuery = window.matchMedia('(max-width: 760px)');
  const tabletQuery = window.matchMedia('(min-width: 761px) and (max-width: 1099px)');
  const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  const motionPreviewRequested = new URLSearchParams(window.location.search).get('motion') === 'preview';
  let storedPreference = null;
  let drawerOpen = false;
  let returnFocusTarget = null;
  let requestedExpanded = null;
  let navigationCommitTimer = null;
  let navigationCleanupTimer = null;

  items.forEach((item, index) => {
    item.style.setProperty('--studio-nav-index', index);
  });

  try {
    storedPreference = window.localStorage.getItem(storageKey);
  } catch {
    storedPreference = null;
  }

  let expanded = storedPreference
    ? storedPreference === 'expanded'
    : !tabletQuery.matches;
  requestedExpanded = expanded;

  const savePreference = () => {
    try {
      window.localStorage.setItem(storageKey, expanded ? 'expanded' : 'collapsed');
      storedPreference = expanded ? 'expanded' : 'collapsed';
    } catch {
      // The sidebar still works when storage is blocked or unavailable.
    }
  };

  const applyState = () => {
    const mobile = mobileQuery.matches;
    const collapsed = !mobile && !expanded;

    shell.classList.toggle('studio-shell--nav-expanded', !collapsed);
    shell.classList.toggle('studio-shell--nav-collapsed', collapsed);
    shell.classList.toggle('studio-shell--drawer-open', mobile && drawerOpen);
    shell.dataset.studioSidebarState = mobile
      ? drawerOpen ? 'drawer-open' : 'drawer-closed'
      : expanded ? 'expanded' : 'collapsed';

    toggle.setAttribute('aria-expanded', String(mobile ? drawerOpen : expanded));
    toggle.setAttribute('aria-label', mobile
      ? 'Close Studio tools'
      : expanded ? 'Collapse Studio sidebar' : 'Expand Studio sidebar');
    drawerOpenButton.setAttribute('aria-expanded', String(mobile && drawerOpen));

    const drawerHidden = mobile && !drawerOpen;
    navigation.toggleAttribute('inert', drawerHidden);
    navigation.setAttribute('aria-hidden', String(drawerHidden));
  };

  const clearNavigationMotion = () => {
    window.clearTimeout(navigationCommitTimer);
    window.clearTimeout(navigationCleanupTimer);
    navigationCommitTimer = null;
    navigationCleanupTimer = null;
    navigation.classList.remove('studio-nav--opening', 'studio-nav--closing');
    navigation.removeAttribute('aria-busy');
  };

  const commitExpandedState = (nextExpanded) => {
    expanded = nextExpanded;
    savePreference();
    applyState();
    announce(`Studio sidebar ${expanded ? 'expanded' : 'collapsed'}.`);
  };

  const transitionNavigation = (nextExpanded) => {
    requestedExpanded = nextExpanded;
    clearNavigationMotion();

    if ((reducedMotionQuery.matches && !motionPreviewRequested) || mobileQuery.matches) {
      commitExpandedState(nextExpanded);
      return;
    }

    navigation.setAttribute('aria-busy', 'true');

    if (nextExpanded) {
      commitExpandedState(true);
      void navigation.offsetWidth;
      navigation.classList.add('studio-nav--opening');
    } else {
      navigation.classList.add('studio-nav--closing');
      navigationCommitTimer = window.setTimeout(() => {
        if (requestedExpanded === false) commitExpandedState(false);
      }, 180);
    }

    navigationCleanupTimer = window.setTimeout(() => {
      navigation.classList.remove('studio-nav--opening', 'studio-nav--closing');
      navigation.removeAttribute('aria-busy');
      navigationCleanupTimer = null;
    }, nextExpanded ? 760 : 620);
  };

  const closeDrawer = (restoreFocus = true) => {
    if (!drawerOpen) return;
    drawerOpen = false;
    applyState();
    announce('Studio tools closed.');

    if (restoreFocus) {
      (returnFocusTarget || drawerOpenButton).focus();
    }
  };

  const openDrawer = () => {
    if (!mobileQuery.matches) return;
    returnFocusTarget = document.activeElement;
    drawerOpen = true;
    applyState();
    announce('Studio tools opened.');
    window.setTimeout(() => toggle.focus(), 50);
  };

  toggle.addEventListener('click', () => {
    if (mobileQuery.matches) {
      closeDrawer();
      return;
    }

    transitionNavigation(!requestedExpanded);
  });

  drawerOpenButton.addEventListener('click', openDrawer);
  drawerCloseButton?.addEventListener('click', () => closeDrawer());

  items.forEach((item, index) => {
    item.addEventListener('click', () => {
      items.forEach((candidate) => {
        const active = candidate === item;
        candidate.classList.toggle('studio-nav__active', active);
        if (active) candidate.setAttribute('aria-current', 'page');
        else candidate.removeAttribute('aria-current');
      });

      if (mobileQuery.matches) closeDrawer();
    });

    item.addEventListener('keydown', (event) => {
      if (!['ArrowUp', 'ArrowDown', 'Home', 'End'].includes(event.key)) return;

      event.preventDefault();
      let nextIndex = index;
      if (event.key === 'ArrowUp') nextIndex = index === 0 ? items.length - 1 : index - 1;
      if (event.key === 'ArrowDown') nextIndex = index === items.length - 1 ? 0 : index + 1;
      if (event.key === 'Home') nextIndex = 0;
      if (event.key === 'End') nextIndex = items.length - 1;
      items[nextIndex].focus();
    });
  });

  const hashItem = items.find((item) => item.hash === window.location.hash);
  if (hashItem) {
    items.forEach((item) => {
      const active = item === hashItem;
      item.classList.toggle('studio-nav__active', active);
      if (active) item.setAttribute('aria-current', 'page');
      else item.removeAttribute('aria-current');
    });
  }

  document.addEventListener('keydown', (event) => {
    const unmodifiedShortcut = !event.altKey && !event.ctrlKey && !event.metaKey && !event.shiftKey;

    if (unmodifiedShortcut && event.code === 'BracketLeft' && !isTextEntryTarget(event.target)) {
      event.preventDefault();
      if (mobileQuery.matches) {
        if (drawerOpen) closeDrawer();
        else openDrawer();
      } else {
        transitionNavigation(!requestedExpanded);
      }
      return;
    }

    if (!mobileQuery.matches || !drawerOpen) return;

    if (event.key === 'Escape') {
      event.preventDefault();
      closeDrawer();
      return;
    }

    if (event.key !== 'Tab') return;
    const focusable = [toggle, ...items].filter((element) => !element.hasAttribute('disabled'));
    const first = focusable[0];
    const last = focusable[focusable.length - 1];

    if (event.shiftKey && document.activeElement === first) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && document.activeElement === last) {
      event.preventDefault();
      first.focus();
    }
  });

  const handleViewportChange = () => {
    clearNavigationMotion();
    if (!mobileQuery.matches) drawerOpen = false;
    if (!storedPreference) expanded = !tabletQuery.matches;
    requestedExpanded = expanded;
    applyState();
  };

  mobileQuery.addEventListener('change', handleViewportChange);
  tabletQuery.addEventListener('change', handleViewportChange);
  applyState();
};

const initWorkspacePanels = () => {
  const stage = document.querySelector('.cinematic-os');
  const shell = document.querySelector('.studio-shell');
  const promo = document.querySelector('#promo-panel');
  const promoToggle = document.querySelector('[data-promo-toggle]');
  const promoToggleLabel = document.querySelector('[data-promo-toggle-label]');
  const aiPanel = document.querySelector('#ai-producer');
  const projectPanel = document.querySelector('#current-project');
  const aiCollapse = document.querySelector('[data-ai-collapse]');
  const aiExpand = document.querySelector('[data-ai-expand]');
  const projectCollapse = document.querySelector('[data-project-collapse]');
  const projectExpand = document.querySelector('[data-project-expand]');
  const panelLaunchers = [...document.querySelectorAll('[data-workspace-panel-open]')];
  const drawerBackdrop = document.querySelector('[data-workspace-drawer-close]');

  if (!stage || !shell || !promo || !promoToggle || !aiPanel || !projectPanel) return;

  shell.setAttribute('aria-keyshortcuts', '[ ]');

  const desktopQuery = window.matchMedia('(min-width: 1100px)');
  const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
  const motionPreviewRequested = new URLSearchParams(window.location.search).get('motion') === 'preview';
  const preferences = readWorkspacePreferences();
  const state = {
    promoHidden: Boolean(preferences.promoHidden),
    aiCollapsed: Boolean(preferences.aiCollapsed),
    projectCollapsed: Boolean(preferences.projectCollapsed),
  };
  let openDrawer = null;
  let drawerReturnFocus = null;
  let aiHologramTimer = null;

  const savePanelState = () => writeWorkspacePreferences(state);

  const stopAiHologram = () => {
    window.clearTimeout(aiHologramTimer);
    aiHologramTimer = null;
    aiPanel.classList.remove('ai-producer--holo-expanding');
  };

  const playAiHologram = () => {
    stopAiHologram();
    if ((reducedMotionQuery.matches && !motionPreviewRequested) || !desktopQuery.matches) return;
    void aiPanel.offsetWidth;
    aiPanel.classList.add('ai-producer--holo-expanding');
    aiHologramTimer = window.setTimeout(stopAiHologram, 1220);
  };

  const alignResponsiveContext = () => {
    if (desktopQuery.matches) return;
    window.requestAnimationFrame(() => {
      (state.promoHidden ? shell : promo).scrollIntoView({ block: 'start', behavior: 'auto' });
    });
  };

  const updateToggle = (control, expanded, label) => {
    if (!control) return;
    control.setAttribute('aria-expanded', String(expanded));
    control.setAttribute('aria-label', label);
  };

  const applyPanelState = () => {
    const desktop = desktopQuery.matches;
    const aiExpanded = desktop ? !state.aiCollapsed : openDrawer === 'ai';
    const projectExpanded = desktop ? !state.projectCollapsed : openDrawer === 'project';

    stage.classList.toggle('cinematic-os--promo-hidden', state.promoHidden);
    shell.classList.toggle('studio-shell--ai-collapsed', desktop && state.aiCollapsed);
    shell.classList.toggle('studio-shell--project-collapsed', desktop && state.projectCollapsed);
    shell.classList.toggle('studio-shell--workspace-drawer-open', !desktop && Boolean(openDrawer));
    shell.dataset.promoPanel = state.promoHidden ? 'hidden' : 'visible';
    shell.dataset.aiPanel = aiExpanded ? 'expanded' : desktop ? 'collapsed' : 'drawer-closed';
    shell.dataset.projectPanel = projectExpanded ? 'expanded' : desktop ? 'collapsed' : 'drawer-closed';

    promo.toggleAttribute('inert', state.promoHidden);
    promo.setAttribute('aria-hidden', String(state.promoHidden));
    promoToggle.setAttribute('aria-expanded', String(!state.promoHidden));
    promoToggle.setAttribute('aria-label', state.promoHidden ? 'Show promotional panel' : 'Hide promotional panel');
    if (promoToggleLabel) promoToggleLabel.textContent = state.promoHidden ? 'Show intro' : 'Hide intro';

    aiPanel.classList.toggle('workspace-panel--drawer-open', !desktop && openDrawer === 'ai');
    projectPanel.classList.toggle('workspace-panel--drawer-open', !desktop && openDrawer === 'project');
    aiPanel.toggleAttribute('inert', !desktop && openDrawer !== 'ai');
    projectPanel.toggleAttribute('inert', !desktop && openDrawer !== 'project');
    aiPanel.setAttribute('aria-hidden', String(!desktop && openDrawer !== 'ai'));
    projectPanel.setAttribute('aria-hidden', String(!desktop && openDrawer !== 'project'));

    updateToggle(aiCollapse, aiExpanded, desktop ? 'Collapse AI Producer' : 'Close AI Producer drawer');
    updateToggle(aiExpand, aiExpanded, 'Open AI Producer');
    updateToggle(projectCollapse, projectExpanded, desktop ? 'Collapse Current Project' : 'Close Current Project drawer');
    updateToggle(projectExpand, projectExpanded, 'Open Current Project');

    panelLaunchers.forEach((launcher) => {
      const type = launcher.dataset.workspacePanelOpen;
      const expanded = openDrawer === type;
      launcher.setAttribute('aria-expanded', String(!desktop && expanded));
      launcher.setAttribute('aria-label', `${expanded ? 'Close' : 'Open'} ${type === 'ai' ? 'AI Producer' : 'Current Project'}`);
    });
  };

  const closePanelDrawer = (restoreFocus = true) => {
    if (!openDrawer) return;
    openDrawer = null;
    applyPanelState();
    announce('Workspace panel closed.');
    if (restoreFocus) (drawerReturnFocus || promoToggle).focus();
  };

  const openPanelDrawer = (type, trigger) => {
    if (desktopQuery.matches) return;
    drawerReturnFocus = trigger;
    openDrawer = type;
    applyPanelState();
    announce(`${type === 'ai' ? 'AI Producer' : 'Current Project'} opened.`);
    const closeControl = type === 'ai' ? aiCollapse : projectCollapse;
    window.setTimeout(() => closeControl?.focus(), 50);
  };

  promoToggle.addEventListener('click', () => {
    state.promoHidden = !state.promoHidden;
    savePanelState();
    applyPanelState();
    alignResponsiveContext();
    announce(`Promotional panel ${state.promoHidden ? 'hidden' : 'shown'}.`);
  });

  aiCollapse?.addEventListener('click', () => {
    if (!desktopQuery.matches) {
      closePanelDrawer();
      return;
    }
    stopAiHologram();
    state.aiCollapsed = true;
    savePanelState();
    applyPanelState();
    announce('AI Producer collapsed.');
    window.setTimeout(() => aiExpand?.focus(), 0);
  });

  aiExpand?.addEventListener('click', () => {
    state.aiCollapsed = false;
    savePanelState();
    applyPanelState();
    playAiHologram();
    announce('AI Producer expanded.');
    window.setTimeout(() => aiCollapse?.focus(), 0);
  });

  projectCollapse?.addEventListener('click', () => {
    if (!desktopQuery.matches) {
      closePanelDrawer();
      return;
    }
    state.projectCollapsed = true;
    savePanelState();
    applyPanelState();
    announce('Current Project collapsed.');
    window.setTimeout(() => projectExpand?.focus(), 0);
  });

  projectExpand?.addEventListener('click', () => {
    state.projectCollapsed = false;
    savePanelState();
    applyPanelState();
    announce('Current Project expanded.');
    window.setTimeout(() => projectCollapse?.focus(), 0);
  });

  panelLaunchers.forEach((launcher) => {
    launcher.addEventListener('click', () => {
      const type = launcher.dataset.workspacePanelOpen;
      if (openDrawer === type) closePanelDrawer();
      else openPanelDrawer(type, launcher);
    });
  });

  drawerBackdrop?.addEventListener('click', () => closePanelDrawer());

  document.addEventListener('keydown', (event) => {
    const unmodifiedShortcut = !event.altKey && !event.ctrlKey && !event.metaKey && !event.shiftKey;

    if (unmodifiedShortcut && event.code === 'BracketRight' && desktopQuery.matches && !isTextEntryTarget(event.target)) {
      event.preventDefault();
      const collapseRightPanels = !(state.aiCollapsed && state.projectCollapsed);
      stopAiHologram();
      state.aiCollapsed = collapseRightPanels;
      state.projectCollapsed = collapseRightPanels;
      savePanelState();
      applyPanelState();
      if (!collapseRightPanels) playAiHologram();
      announce(`Right workspace panels ${collapseRightPanels ? 'collapsed' : 'expanded'}.`);
      return;
    }

    if (event.key === 'Escape' && openDrawer) {
      event.preventDefault();
      closePanelDrawer();
    }
  });

  desktopQuery.addEventListener('change', () => {
    stopAiHologram();
    openDrawer = null;
    applyPanelState();
  });

  applyPanelState();
  if (state.promoHidden) window.setTimeout(alignResponsiveContext, 0);
};

const initTimelineResize = () => {
  const editor = document.querySelector('.editor-workspace');
  const header = document.querySelector('.editor-workspace__header');
  const preview = document.querySelector('.editor-preview');
  const timeline = document.querySelector('#studio-timeline');
  const handle = document.querySelector('[data-timeline-resizer]');

  if (!editor || !header || !preview || !timeline || !handle) return;

  const responsiveQuery = window.matchMedia('(max-width: 1099px)');
  const storedHeight = Number(readWorkspacePreferences().timelineHeight);
  let currentHeight = Number.isFinite(storedHeight) && storedHeight > 0 ? storedHeight : 0;
  let pointerStartY = 0;
  let pointerStartHeight = 0;
  let activePointerId = null;

  const getBounds = () => {
    const editorHeight = editor.getBoundingClientRect().height;
    const headerHeight = header.getBoundingClientRect().height;
    const handleHeight = Math.max(8, handle.getBoundingClientRect().height);
    const minimum = Math.max(118, Math.round(editorHeight * .22));
    const previewMinimum = Math.max(150, Math.round(editorHeight * .27));
    const maximum = Math.max(minimum, Math.round(editorHeight - headerHeight - handleHeight - previewMinimum));
    return { minimum, maximum };
  };

  const applyHeight = (nextHeight, persist = false) => {
    if (responsiveQuery.matches) {
      handle.tabIndex = -1;
      handle.setAttribute('aria-disabled', 'true');
      editor.style.removeProperty('--timeline-height');
      return;
    }

    const { minimum, maximum } = getBounds();
    currentHeight = Math.min(maximum, Math.max(minimum, Math.round(nextHeight || editor.getBoundingClientRect().height * .42)));
    editor.style.setProperty('--timeline-height', `${currentHeight}px`);
    handle.tabIndex = 0;
    handle.setAttribute('aria-disabled', 'false');
    handle.setAttribute('aria-valuemin', String(minimum));
    handle.setAttribute('aria-valuemax', String(maximum));
    handle.setAttribute('aria-valuenow', String(currentHeight));
    handle.setAttribute('aria-valuetext', `Timeline height ${currentHeight} pixels`);
    if (persist) writeWorkspacePreferences({ timelineHeight: currentHeight });
  };

  handle.addEventListener('pointerdown', (event) => {
    if (responsiveQuery.matches) return;
    activePointerId = event.pointerId;
    pointerStartY = event.clientY;
    pointerStartHeight = timeline.getBoundingClientRect().height;
    handle.classList.add('is-resizing');
    event.preventDefault();
  });

  const resizeFromPointer = (event) => {
    if (activePointerId !== event.pointerId) return;
    applyHeight(pointerStartHeight - (event.clientY - pointerStartY));
  };

  const finishResize = (event) => {
    if (activePointerId !== event.pointerId) return;
    activePointerId = null;
    handle.classList.remove('is-resizing');
    writeWorkspacePreferences({ timelineHeight: currentHeight });
  };

  window.addEventListener('pointermove', resizeFromPointer);
  window.addEventListener('pointerup', finishResize);
  window.addEventListener('pointercancel', finishResize);

  handle.addEventListener('keydown', (event) => {
    if (responsiveQuery.matches || !['ArrowUp', 'ArrowDown', 'PageUp', 'PageDown', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    const { minimum, maximum } = getBounds();
    let nextHeight = currentHeight;
    if (event.key === 'ArrowUp') nextHeight += 10;
    if (event.key === 'ArrowDown') nextHeight -= 10;
    if (event.key === 'PageUp') nextHeight += 30;
    if (event.key === 'PageDown') nextHeight -= 30;
    if (event.key === 'Home') nextHeight = minimum;
    if (event.key === 'End') nextHeight = maximum;
    applyHeight(nextHeight, true);
    announce(`Timeline height ${currentHeight} pixels.`);
  });

  const syncResponsiveState = () => window.requestAnimationFrame(() => applyHeight(currentHeight));
  responsiveQuery.addEventListener('change', syncResponsiveState);
  window.addEventListener('resize', syncResponsiveState);
  window.requestAnimationFrame(() => applyHeight(currentHeight));
};

initEcosystemTabs();
initAssetTurntables();
initAiProducer();
initPlayback();
initHeaderUtilities();
initCreatorPulse();
initCollaborationHub();
initActionAnnouncements();
initVisibilityAwareness();
initTerminalMotion();
initStudioNavigation();
initWorkspacePanels();
initTimelineResize();

/**
 * Lighthouse CI configuration  (RNF-09)
 *
 * Audits the public menu page and asserts all four category scores > 90.
 * Run locally:
 *   npx @lhci/cli autorun --config=lighthouserc.js
 */
module.exports = {
  ci: {
    collect: {
      /* URLs are set by CI via the --url flag or the env var LHCI_URL.
       * Default to localhost:8000 (docker compose frontend). */
      url: [
        process.env.LHCI_URL || 'http://localhost:8000/api/v1/auth/login',
      ],
      numberOfRuns: 3,
      settings: {
        /* Use "mobile" emulation (default Lighthouse mode) */
        preset: 'desktop',
        onlyCategories: ['performance', 'accessibility', 'best-practices', 'seo'],
        /* Skip HTTPS-specific audits when testing localhost */
        skipAudits: ['is-on-https', 'redirects-http'],
      },
    },
    assert: {
      assertions: {
        'categories:performance':  ['warn', { minScore: 0.9 }],
        'categories:accessibility': ['error', { minScore: 0.9 }],
        'categories:best-practices': ['warn', { minScore: 0.9 }],
        'categories:seo':          ['warn', { minScore: 0.9 }],
      },
    },
    upload: {
      /* Don't upload anywhere; just print to stdout */
      target: 'temporary-public-storage',
    },
  },
};

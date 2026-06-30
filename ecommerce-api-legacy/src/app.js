'use strict';

const { createApp } = require('./appFactory');
const { config } = require('./config');
const logger = require('./logger');

// Entry point: build the app explicitly, then listen. Port comes from config
// (env PORT, dev default 3000) so the app can boot on a free port.
createApp()
  .then(({ app }) => {
    app.listen(config.port, () => {
      logger.info(`LMS API rodando na porta ${config.port}...`);
    });
  })
  .catch((err) => {
    logger.error('Falha ao iniciar a aplicação:', err && err.message);
    process.exit(1);
  });

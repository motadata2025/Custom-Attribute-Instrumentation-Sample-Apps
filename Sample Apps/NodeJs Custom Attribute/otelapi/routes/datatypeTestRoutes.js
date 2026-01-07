const express = require('express');
const router = express.Router();
const DatatypeTestController = require('../controllers/datatypeTestController');

/**
 * @swagger
 * /datatypes:
 *   get:
 *     summary: Test OpenTelemetry span attribute data types
 *     tags: [Testing]
 *     responses:
 *       200:
 *         description: Data type testing completed
 */
router.get('/', DatatypeTestController.testDataTypes);

module.exports = router;


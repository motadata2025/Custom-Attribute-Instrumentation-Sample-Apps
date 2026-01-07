const express = require('express');
const router = express.Router();
const AttributeTestController = require('../controllers/attributeTestController');

/**
 * @swagger
 * /attributes/test:
 *   get:
 *     summary: Test OpenTelemetry custom attributes using MotadataDynamicInstrumentation utility
 *     tags: [Testing]
 *     description: |
 *       Tests all supported data types for OpenTelemetry span attributes:
 *       - string
 *       - number (integer and decimal)
 *       - boolean
 *       - string[]
 *       - number[]
 *       - boolean[]
 *       
 *       All attributes are automatically prefixed with "apm."
 *     responses:
 *       200:
 *         description: Attribute testing completed successfully
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: true
 *                 message:
 *                   type: string
 *                   example: All data types tested successfully using MotadataDynamicInstrumentation
 *                 attributes_set:
 *                   type: object
 *                   description: All attributes that were set on the span
 *                 supported_types:
 *                   type: array
 *                   items:
 *                     type: string
 *                   example: ["string", "number", "boolean", "string[]", "number[]", "boolean[]"]
 *                 edge_cases_tested:
 *                   type: array
 *                   items:
 *                     type: string
 *                 note:
 *                   type: string
 *                   example: All attributes are prefixed with "apm." automatically
 *       500:
 *         description: Error occurred during testing
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 success:
 *                   type: boolean
 *                   example: false
 *                 message:
 *                   type: string
 *                 error:
 *                   type: string
 */
router.get('/test', AttributeTestController.testAttributes);

module.exports = router;


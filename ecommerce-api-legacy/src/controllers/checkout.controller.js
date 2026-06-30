'use strict';

const passwordService = require('../services/password.service');
const paymentService = require('../services/payment.service');

// Orchestrates the checkout flow. No SQL, no inline payment logic — it
// validates input, calls models/services, and shapes the response. Status
// branches are preserved from the legacy handler (400/404/400-denied/200).
class CheckoutController {
  constructor({ userModel, courseModel, enrollmentModel, paymentModel, auditLogModel }) {
    this.userModel = userModel;
    this.courseModel = courseModel;
    this.enrollmentModel = enrollmentModel;
    this.paymentModel = paymentModel;
    this.auditLogModel = auditLogModel;
  }

  checkout = async (req, res) => {
    const name = req.body.usr;
    const email = req.body.eml;
    const password = req.body.pwd;
    const courseId = req.body.c_id;
    const card = req.body.card;

    if (!name || !email || !courseId || !card) {
      return res.status(400).send('Bad Request');
    }

    const course = await this.courseModel.findActiveById(courseId);
    if (!course) return res.status(404).send('Curso não encontrado');

    let user = await this.userModel.findByEmail(email);
    if (!user) {
      const passHash = passwordService.hash(password || '123456');
      user = await this.userModel.create({ name, email, passHash });
    }

    const { status } = paymentService.authorize(card, course.price);
    if (status === 'DENIED') return res.status(400).send('Pagamento recusado');

    const enrollment = await this.enrollmentModel.create({ userId: user.id, courseId });
    await this.paymentModel.create({ enrollmentId: enrollment.id, amount: course.price, status });
    await this.auditLogModel.record(`Checkout curso ${courseId} por ${user.id}`);

    return res.status(200).json({ msg: 'Sucesso', enrollment_id: enrollment.id });
  };
}

module.exports = { CheckoutController };

'use strict';

class ReportController {
  constructor({ reportModel }) {
    this.reportModel = reportModel;
  }

  financial = async (req, res) => {
    const report = await this.reportModel.financial();
    return res.status(200).json(report);
  };
}

module.exports = { ReportController };

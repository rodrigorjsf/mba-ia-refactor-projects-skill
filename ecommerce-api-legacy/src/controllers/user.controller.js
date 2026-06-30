'use strict';

class UserController {
  constructor({ userModel }) {
    this.userModel = userModel;
  }

  // Destructive: reachable only past the admin-auth middleware. Cascades to
  // dependents in the model so no orphan rows remain.
  remove = async (req, res) => {
    await this.userModel.deleteWithDependents(req.params.id);
    return res.status(200).send('Usuário deletado (matrículas e pagamentos removidos em transação).');
  };
}

module.exports = { UserController };

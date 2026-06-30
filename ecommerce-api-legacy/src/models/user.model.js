'use strict';

// User persistence. Only this layer touches the users table.
class UserModel {
  constructor(db) {
    this.db = db;
  }

  findByEmail(email) {
    return this.db.get('SELECT id, name, email FROM users WHERE email = ?', [email]);
  }

  async create({ name, email, passHash }) {
    const { lastID } = await this.db.run(
      'INSERT INTO users (name, email, pass) VALUES (?, ?, ?)',
      [name, email, passHash]
    );
    return { id: lastID, name, email };
  }

  // Delete a user and its dependents in one transaction (audit: MEDIUM
  // referential integrity — no more orphaned enrollments/payments).
  async deleteWithDependents(id) {
    await this.db.exec('BEGIN');
    try {
      await this.db.run(
        'DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)',
        [id]
      );
      await this.db.run('DELETE FROM enrollments WHERE user_id = ?', [id]);
      const { changes } = await this.db.run('DELETE FROM users WHERE id = ?', [id]);
      await this.db.exec('COMMIT');
      return { deleted: changes };
    } catch (err) {
      await this.db.exec('ROLLBACK');
      throw err;
    }
  }
}

module.exports = { UserModel };

'use strict';

// Financial report read model. Replaces the N+1 cursor pyramid (audit: MEDIUM)
// with a single LEFT JOIN, grouped in memory. Output shape is preserved exactly:
//   [{ course, revenue, students: [{ student, paid }] }]
class ReportModel {
  constructor(db) {
    this.db = db;
  }

  async financial() {
    const rows = await this.db.all(
      `SELECT c.id          AS course_id,
              c.title       AS course,
              e.id          AS enrollment_id,
              u.name        AS student,
              p.amount      AS amount,
              p.status      AS status
         FROM courses c
         LEFT JOIN enrollments e ON e.course_id = c.id
         LEFT JOIN users u       ON u.id = e.user_id
         LEFT JOIN payments p    ON p.enrollment_id = e.id
        ORDER BY c.id`,
      []
    );

    const byCourse = new Map();
    for (const r of rows) {
      if (!byCourse.has(r.course_id)) {
        byCourse.set(r.course_id, { course: r.course, revenue: 0, students: [] });
      }
      const entry = byCourse.get(r.course_id);
      if (r.enrollment_id != null) {
        if (r.status === 'PAID') entry.revenue += r.amount;
        entry.students.push({ student: r.student || 'Unknown', paid: r.amount != null ? r.amount : 0 });
      }
    }
    return Array.from(byCourse.values());
  }
}

module.exports = { ReportModel };

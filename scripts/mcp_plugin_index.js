const { Pool } = require('pg');

const requiredEnv = ['PGHOST', 'PGPORT', 'PGUSER', 'PGPASSWORD', 'PGDATABASE'];
for (const key of requiredEnv) {
  if (!process.env[key]) {
    throw new Error(`Environment variable ${key} must be set for database connection.`);
  }
}
const pool = new Pool({
  host: process.env.PGHOST,
  port: Number(process.env.PGPORT),
  user: process.env.PGUSER,
  password: process.env.PGPASSWORD,
  database: process.env.PGDATABASE,
});

async function query(text, params) {
  const client = await pool.connect();
  try {
    const res = await client.query(text, params);
    return res.rows;
  } finally {
    client.release();
  }
}

async function getMcps() {
  return query('SELECT * FROM mcps');
}

async function getSchema() {
  const tables = await query(`
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema = 'public' AND table_type = 'BASE TABLE';
  `);
  const schema = {};
  for (const { table_name } of tables) {
    const columns = await query(`
      SELECT column_name, data_type, is_nullable
      FROM information_schema.columns
      WHERE table_name = $1;
    `, [table_name]);
    schema[table_name] = columns;
  }
  return schema;
}

module.exports = {
  query,
  getMcps,
  getSchema,
};

if (require.main === module) {
  getSchema().then(schema => {
    console.dir(schema, { depth: null });
    process.exit(0);
  }).catch(err => {
    console.error(err);
    process.exit(1);
  });
} 
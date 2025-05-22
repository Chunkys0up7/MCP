# Recommended PostgreSQL Setup for Production/Later Phases

For a more robust and secure setup, especially when moving beyond the initial pilot phase, it's highly recommended to use a dedicated PostgreSQL user and database for the application.

## 1. Create a Dedicated Database User (Role)

Instead of using the default `postgres` superuser for the application, create a specific user with only the necessary permissions.

**Connect to PostgreSQL (e.g., using `psql -U postgres`):**

```sql
-- Replace 'mcp_app_user' with your desired username
-- Replace 'a_strong_password_here' with a strong, unique password
CREATE USER mcp_app_user WITH PASSWORD 'a_strong_password_here';
```

## 2. Create a Dedicated Database

Create a database specifically for this application and assign the new user as its owner.

```sql
-- Replace 'mcp_application_db' with your desired database name
-- Ensure 'mcp_app_user' matches the user created above
CREATE DATABASE mcp_application_db OWNER mcp_app_user;
```

## 3. Grant Privileges (Optional but often useful)

While owning the database grants many privileges, you might want to explicitly grant all standard privileges on that database to the user.

```sql
GRANT ALL PRIVILEGES ON DATABASE mcp_application_db TO mcp_app_user;
```

## 4. Update `.env` Configuration

Update your project's `.env` file with the credentials for this new user and database:

```env
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=mcp_application_db # Your new database name
POSTGRES_USER=mcp_app_user     # Your new user
POSTGRES_PASSWORD=a_strong_password_here # The password for the new user
```

## 5. `pg_hba.conf` and `postgresql.conf`

*   **`listen_addresses` in `postgresql.conf`:** Ensure PostgreSQL is listening on the correct network interfaces. For local development, `localhost` is usually fine. For production, this might need to be a specific IP address or `*` (with appropriate firewall rules).
*   **`pg_hba.conf`:** This file controls client authentication. Ensure there's a line allowing your `mcp_app_user` to connect to `mcp_application_db` from the application server's IP address (or `127.0.0.1`/`::1` for local connections). Use a secure authentication method like `scram-sha-256`.

    Example for `pg_hba.conf`:
    ```
    # TYPE  DATABASE             USER          ADDRESS        METHOD
    host    mcp_application_db   mcp_app_user  127.0.0.1/32   scram-sha-256
    host    mcp_application_db   mcp_app_user  ::1/128        scram-sha-256
    # Add a line for your application server's IP if it's remote
    # host    mcp_application_db   mcp_app_user  <app_server_ip>/32  scram-sha-256
    ```

*   **Restart PostgreSQL Server:** If you modify `postgresql.conf` or `pg_hba.conf`, the PostgreSQL server must be restarted for changes to take effect.

## Benefits of this Approach:

*   **Security (Principle of Least Privilege):** The application connects with a user that only has permissions for its own database, reducing the potential impact if the application's credentials are compromised.
*   **Isolation:** Separates your application's data and schema from other databases or system tables.
*   **Clarity:** Makes it clear which database and user belong to which application. 
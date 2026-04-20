-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL,
    full_name TEXT NOT NULL,
    email TEXT,
    role TEXT DEFAULT 'staff',
    is_active INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_login TIMESTAMP
);

-- Roles and permissions
CREATE TABLE IF NOT EXISTS permissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT UNIQUE NOT NULL,
    description TEXT
);

CREATE TABLE IF NOT EXISTS role_permissions (
    role TEXT NOT NULL,
    permission_id INTEGER,
    FOREIGN KEY (permission_id) REFERENCES permissions (id)
);

-- Audit logs
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action TEXT NOT NULL,
    table_name TEXT,
    record_id INTEGER,
    old_value TEXT,
    new_value TEXT,
    ip_address TEXT,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

-- Customers table (enhanced)
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    phone TEXT,
    email TEXT,
    address TEXT,
    gst_number TEXT,
    pan_number TEXT,
    opening_balance REAL DEFAULT 0,
    credit_limit REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Products table with tax info
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    description TEXT,
    hsn_code TEXT,
    price REAL NOT NULL,
    cost_price REAL,
    tax_rate_cgst REAL DEFAULT 0,
    tax_rate_sgst REAL DEFAULT 0,
    tax_rate_igst REAL DEFAULT 0,
    tax_category TEXT DEFAULT 'gst',
    unit TEXT DEFAULT 'pcs',
    stock_quantity REAL DEFAULT 0,
    reorder_level REAL DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Invoices table (enhanced)
CREATE TABLE IF NOT EXISTS invoices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_number TEXT UNIQUE NOT NULL,
    customer_id INTEGER,
    invoice_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP,
    subtotal REAL NOT NULL,
    cgst_total REAL DEFAULT 0,
    sgst_total REAL DEFAULT 0,
    igst_total REAL DEFAULT 0,
    tax_total REAL NOT NULL,
    grand_total REAL NOT NULL,
    paid_amount REAL DEFAULT 0,
    balance_due REAL,
    status TEXT DEFAULT 'pending', -- pending, paid, overdue, cancelled
    payment_status TEXT DEFAULT 'unpaid',
    notes TEXT,
    terms TEXT,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (customer_id) REFERENCES customers (id),
    FOREIGN KEY (created_by) REFERENCES users (id)
);

-- Invoice items (enhanced)
CREATE TABLE IF NOT EXISTS invoice_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER,
    product_id INTEGER,
    quantity REAL NOT NULL,
    unit_price REAL NOT NULL,
    cgst_rate REAL DEFAULT 0,
    sgst_rate REAL DEFAULT 0,
    igst_rate REAL DEFAULT 0,
    cgst_amount REAL DEFAULT 0,
    sgst_amount REAL DEFAULT 0,
    igst_amount REAL DEFAULT 0,
    total REAL NOT NULL,
    FOREIGN KEY (invoice_id) REFERENCES invoices (id),
    FOREIGN KEY (product_id) REFERENCES products (id)
);

-- Invoice payments tracking
CREATE TABLE IF NOT EXISTS invoice_payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    invoice_id INTEGER,
    amount REAL NOT NULL,
    payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    payment_method TEXT,
    reference_number TEXT,
    notes TEXT,
    recorded_by INTEGER,
    FOREIGN KEY (invoice_id) REFERENCES invoices (id),
    FOREIGN KEY (recorded_by) REFERENCES users (id)
);

-- Expenses tracking
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    expense_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    category TEXT NOT NULL,
    description TEXT,
    amount REAL NOT NULL,
    payment_method TEXT,
    receipt_number TEXT,
    vendor_name TEXT,
    created_by INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users (id)
);

-- Tax configuration
CREATE TABLE IF NOT EXISTS tax_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tax_type TEXT NOT NULL, -- cgst, sgst, igst, cess
    rate REAL NOT NULL,
    effective_from TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    is_active INTEGER DEFAULT 1
);

-- Settings table (extended)
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    setting_key TEXT UNIQUE NOT NULL,
    setting_value TEXT,
    setting_type TEXT DEFAULT 'string',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert default settings
INSERT OR IGNORE INTO settings (setting_key, setting_value, setting_type) VALUES 
    ('business_name', 'My Business', 'string'),
    ('business_address', '123 Business St, City, Country', 'string'),
    ('business_phone', '+1234567890', 'string'),
    ('business_email', 'info@mybusiness.com', 'string'),
    ('business_gst', '27AAABC1234F1Z', 'string'),
    ('business_pan', 'AAAAA1234A', 'string'),
    ('currency_symbol', '₹', 'string'),
    ('invoice_prefix', 'INV', 'string'),
    ('invoice_terms', 'Thank you for your business!', 'string'),
    ('default_cgst', '9', 'float'),
    ('default_sgst', '9', 'float'),
    ('default_igst', '18', 'float'),
    ('smtp_host', '', 'string'),
    ('smtp_port', '587', 'integer'),
    ('smtp_user', '', 'string'),
    ('smtp_password', '', 'string'),
    ('smtp_from_email', '', 'string'),
    ('ui_theme', 'light', 'string'),
    ('backup_enabled', '0', 'boolean'),
    ('backup_path', '', 'string'),
    ('auto_backup_frequency', 'daily', 'string');

-- Insert default permissions
INSERT OR IGNORE INTO permissions (name, description) VALUES 
    ('view_dashboard', 'View dashboard'),
    ('manage_customers', 'Add/edit/delete customers'),
    ('manage_products', 'Add/edit/delete products'),
    ('manage_invoices', 'Create/edit invoices'),
    ('delete_invoices', 'Delete invoices'),
    ('manage_expenses', 'Add/edit/delete expenses'),
    ('view_reports', 'View financial reports'),
    ('manage_settings', 'Modify system settings'),
    ('manage_users', 'Add/edit/delete users'),
    ('view_audit_logs', 'View audit logs'),
    ('manage_backup', 'Backup and restore database');

-- Insert default admin user (password: Admin@123)
INSERT OR IGNORE INTO users (username, password_hash, full_name, role, is_active) VALUES 
    ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYQiE/fQJuy', 'Administrator', 'admin', 1);

-- Add new settings for SMTP, Bank Details, and Logo
INSERT OR IGNORE INTO settings (setting_key, setting_value, setting_type) VALUES 
    -- Bank Details
    ('bank_name', '', 'string'),
    ('bank_account_name', '', 'string'),
    ('bank_account_number', '', 'string'),
    ('bank_ifsc', '', 'string'),
    ('bank_branch', '', 'string'),
    ('bank_upi_id', '', 'string'),
    
    -- SMTP Settings
    ('smtp_host', 'smtp.gmail.com', 'string'),
    ('smtp_port', '587', 'integer'),
    ('smtp_user', '', 'string'),
    ('smtp_password', '', 'string'),
    ('smtp_from_email', '', 'string'),
    ('smtp_use_tls', '1', 'boolean'),
    
    -- Logo
    ('company_logo', '', 'blob');
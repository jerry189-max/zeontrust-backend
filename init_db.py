import sqlite3
import os

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'database', 'Zeontrust_wallet.db')

def init_database():
    # Ensure database directory exists
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()
    
    # ==================== USERS & AUTH ====================
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        is_active BOOLEAN DEFAULT 1,
        is_admin BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_login TIMESTAMP
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT NOT NULL,
        expires_at TIMESTAMP NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS security_settings (
        user_id INTEGER PRIMARY KEY,
        password_lock_enabled BOOLEAN DEFAULT 1,
        session_timeout_minutes INTEGER DEFAULT 1440,
        two_factor_enabled BOOLEAN DEFAULT 0,
        pin_enabled BOOLEAN DEFAULT 0,
        pin_hash TEXT,
        two_factor_secret TEXT,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # ==================== WALLETS ====================
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS wallets (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        wallet_name TEXT NOT NULL,
        mnemonic_encrypted TEXT,
        is_backed_up BOOLEAN DEFAULT 0,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS network_accounts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wallet_id INTEGER NOT NULL,
        network TEXT NOT NULL,
        address TEXT NOT NULL,
        private_key_encrypted TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (wallet_id) REFERENCES wallets(id)
    )''')
    
    # ==================== TRANSACTIONS ====================
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        wallet_id INTEGER NOT NULL,
        network TEXT NOT NULL,
        tx_hash TEXT UNIQUE NOT NULL,
        from_address TEXT NOT NULL,
        to_address TEXT NOT NULL,
        amount TEXT NOT NULL,
        token_address TEXT,
        token_symbol TEXT,
        fee TEXT,
        status TEXT DEFAULT 'pending',
        block_number INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (wallet_id) REFERENCES wallets(id)
    )''')
    
    # ==================== TOKENS ====================
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS custom_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        network TEXT NOT NULL,
        contract_address TEXT NOT NULL,
        token_name TEXT NOT NULL,
        token_symbol TEXT NOT NULL,
        decimals INTEGER NOT NULL,
        logo_url TEXT,
        added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        UNIQUE(user_id, network, contract_address)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS token_verification_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        network TEXT NOT NULL,
        contract_address TEXT NOT NULL,
        token_name TEXT NOT NULL,
        token_symbol TEXT NOT NULL,
        decimals INTEGER NOT NULL,
        website TEXT,
        email TEXT,
        twitter TEXT,
        telegram TEXT,
        discord TEXT,
        logo_url TEXT,
        description TEXT,
        status TEXT DEFAULT 'pending',
        admin_notes TEXT,
        submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        reviewed_at TIMESTAMP,
        reviewed_by INTEGER,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS verified_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        network TEXT NOT NULL,
        contract_address TEXT NOT NULL,
        token_name TEXT NOT NULL,
        token_symbol TEXT NOT NULL,
        decimals INTEGER NOT NULL,
        logo_url TEXT,
        website TEXT,
        category TEXT,
        risk_level TEXT DEFAULT 'low',
        is_active BOOLEAN DEFAULT 1,
        verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        verified_by INTEGER,
        UNIQUE(network, contract_address)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS token_categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        icon TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # ==================== RESERVE TOKENS ====================
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS reserve_tokens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        network TEXT NOT NULL,
        contract_address TEXT NOT NULL,
        token_name TEXT NOT NULL,
        token_symbol TEXT NOT NULL,
        decimals INTEGER NOT NULL,
        total_supply TEXT NOT NULL,
        balance TEXT NOT NULL,
        is_mintable BOOLEAN DEFAULT 1,
        is_burnable BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by INTEGER
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS reserve_transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        token_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        amount TEXT NOT NULL,
        from_address TEXT,
        to_address TEXT,
        tx_hash TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (token_id) REFERENCES reserve_tokens(id)
    )''')
    
    # ==================== LOANS ====================
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS loan_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        wallet_id INTEGER NOT NULL,
        network TEXT NOT NULL,
        token TEXT NOT NULL,
        amount TEXT NOT NULL,
        duration_days INTEGER NOT NULL,
        interest_rate REAL,
        total_payable TEXT,
        purpose TEXT,
        status TEXT DEFAULT 'pending',
        approved_by INTEGER,
        approved_at TIMESTAMP,
        repaid_amount TEXT DEFAULT '0',
        is_repaid BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (wallet_id) REFERENCES wallets(id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS flash_loans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        wallet_id INTEGER NOT NULL,
        network TEXT NOT NULL,
        token TEXT NOT NULL,
        amount TEXT NOT NULL,
        fee TEXT,
        status TEXT DEFAULT 'pending',
        approved_by INTEGER,
        approved_at TIMESTAMP,
        repaid_at TIMESTAMP,
        tx_hash TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # ==================== DEX POOLS ====================
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS pools (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        network TEXT NOT NULL,
        token_a_address TEXT NOT NULL,
        token_a_symbol TEXT NOT NULL,
        token_b_address TEXT NOT NULL,
        token_b_symbol TEXT NOT NULL,
        reserve_a TEXT NOT NULL,
        reserve_b TEXT NOT NULL,
        total_liquidity TEXT NOT NULL,
        fee_percent REAL DEFAULT 0.3,
        is_active BOOLEAN DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by INTEGER,
        UNIQUE(network, token_a_address, token_b_address)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS liquidity_positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        pool_id INTEGER NOT NULL,
        user_id INTEGER NOT NULL,
        wallet_id INTEGER NOT NULL,
        lp_token_address TEXT,
        lp_token_amount TEXT NOT NULL,
        amount_a TEXT NOT NULL,
        amount_b TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (pool_id) REFERENCES pools(id),
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS swaps (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        wallet_id INTEGER NOT NULL,
        pool_id INTEGER NOT NULL,
        from_token TEXT NOT NULL,
        to_token TEXT NOT NULL,
        from_amount TEXT NOT NULL,
        to_amount TEXT NOT NULL,
        fee TEXT,
        tx_hash TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (pool_id) REFERENCES pools(id)
    )''')
    
    # ==================== STAKING ====================
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS staking_positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        wallet_id INTEGER NOT NULL,
        network TEXT NOT NULL,
        amount TEXT NOT NULL,
        resource_type TEXT DEFAULT 'ENERGY',
        duration_days INTEGER DEFAULT 90,
        tx_hash TEXT,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        unlocked_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (wallet_id) REFERENCES wallets(id)
    )''')
    
    # ==================== ADDRESS BOOK ====================
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS address_book (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        address TEXT NOT NULL,
        network TEXT NOT NULL,
        notes TEXT,
        favorite BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # ==================== MULTISIG ====================
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS multisig_wallets (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        owners TEXT NOT NULL,
        threshold INTEGER NOT NULL,
        network TEXT NOT NULL,
        address TEXT NOT NULL,
        status TEXT DEFAULT 'active',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        created_by INTEGER,
        FOREIGN KEY (created_by) REFERENCES users(id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS proposals (
        id TEXT PRIMARY KEY,
        multisig_id TEXT NOT NULL,
        creator TEXT NOT NULL,
        to_address TEXT NOT NULL,
        amount TEXT NOT NULL,
        token_address TEXT,
        description TEXT,
        signatures TEXT,
        required_signatures INTEGER DEFAULT 2,
        status TEXT DEFAULT 'pending',
        executed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (multisig_id) REFERENCES multisig_wallets(id)
    )''')
    
    # ==================== DAPP ====================
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS dapp_favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        url TEXT NOT NULL,
        network TEXT NOT NULL,
        icon TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS connection_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        wallet_id INTEGER NOT NULL,
        dapp_url TEXT NOT NULL,
        dapp_name TEXT NOT NULL,
        network TEXT NOT NULL,
        connection_id TEXT NOT NULL,
        connected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        disconnected_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # ==================== NOTIFICATIONS ====================
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS notifications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        data TEXT,
        is_read BOOLEAN DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id)
    )''')
    
    # ==================== ADMIN LOGS ====================
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS admin_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        admin_id INTEGER NOT NULL,
        action TEXT NOT NULL,
        target_type TEXT,
        target_id INTEGER,
        details TEXT,
        ip_address TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (admin_id) REFERENCES users(id)
    )''')
    
    # ==================== SETTINGS ====================
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # ==================== BACKUP HISTORY ====================
    
    cursor.execute('''CREATE TABLE IF NOT EXISTS backup_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        wallet_id INTEGER NOT NULL,
        backup_type TEXT NOT NULL,
        backup_hash TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (wallet_id) REFERENCES wallets(id)
    )''')
    
    # ==================== DEFAULT DATA ====================
    
    # Insert default settings
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ('min_loan_amount', '1'))
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ('max_loan_amount', '1000000'))
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ('max_loan_duration', '90'))
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ('transfer_fee_percent', '0.01'))
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ('swap_fee_percent', '0.3'))
    cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", ('default_interest_rate', '5'))
    
    # Insert default admin user (password: admin123)
    import hashlib
    admin_password_hash = hashlib.sha256('admin123'.encode()).hexdigest()
    cursor.execute('''INSERT OR IGNORE INTO users (username, email, password_hash, is_admin)
        VALUES (?, ?, ?, ?)''', ('admin', 'admin@Zeontrustwallet.com', admin_password_hash, 1))
    
    # Insert default token categories
    cursor.execute("INSERT OR IGNORE INTO token_categories (name, icon) VALUES (?, ?)", ('DeFi', '🏦'))
    cursor.execute("INSERT OR IGNORE INTO token_categories (name, icon) VALUES (?, ?)", ('NFT', '🎨'))
    cursor.execute("INSERT OR IGNORE INTO token_categories (name, icon) VALUES (?, ?)", ('Gaming', '🎮'))
    cursor.execute("INSERT OR IGNORE INTO token_categories (name, icon) VALUES (?, ?)", ('Meme', '😂'))
    cursor.execute("INSERT OR IGNORE INTO token_categories (name, icon) VALUES (?, ?)", ('Infrastructure', '🏗️'))
    
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")

if __name__ == '__main__':
    init_database()
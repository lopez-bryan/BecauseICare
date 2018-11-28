CREATE TABLE users (uid INT AUTO_INCREMENT PRIMARY KEY,
					username VARCHAR(20) NOT NULL,
					password VARCHAR(100) NOT NULL,
					email VARCHAR(50) NOT NULL,
					settings BLOB(16383),
					tracking BLOB(16383));

CREATE TABLE items (
	iid INT AUTO_INCREMENT PRIMARY KEY,
	userid INT,
	item VARCHAR(100) NOT NULL,
	finished_item VARCHAR(100),
	FOREIGN KEY (userid) REFERENCES users(uid)
	);

const mongoose = require('mongoose');
const User = require('./models/User');
require('dotenv').config();

async function initUsers() {
  try {
    // Connect to MongoDB
    await mongoose.connect(process.env.MONGODB_URL);
    console.log('Connected to MongoDB');

    // Create admin user
    const adminExists = await User.findOne({ username: 'admin' });
    if (!adminExists) {
      const bcrypt = require('bcryptjs');
      const hashedPassword = await bcrypt.hash('admin123', 10);
      const admin = new User({
        username: 'admin',
        password: hashedPassword,
        role: 'admin'
      });
      await admin.save();
      console.log('Admin user created');
    } else {
      console.log('Admin user already exists');
    }

    // Create regular user
    const userExists = await User.findOne({ username: 'user' });
    if (!userExists) {
      const bcrypt = require('bcryptjs');
      const hashedPassword = await bcrypt.hash('user123', 10);
      const user = new User({
        username: 'user',
        password: hashedPassword,
        role: 'user'
      });
      await user.save();
      console.log('Regular user created');
    } else {
      console.log('Regular user already exists');
    }

    console.log('User initialization complete');
  } catch (error) {
    console.error('Error initializing users:', error);
  } finally {
    await mongoose.connection.close();
    console.log('Database connection closed');
  }
}

initUsers();
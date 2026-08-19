const mongoose = require("mongoose");

const connectDB = async () => {

    console.log("Step 1: connectDB() called");

    try {

        console.log("Step 2: Trying to connect...");

        await mongoose.connect(process.env.MONGO_URI);

        console.log("✅ Step 3: MongoDB Connected");

    } catch (error) {
    console.log("❌ Database Connection Failed");
    console.log("Name:", error.name);
    console.log("Message:", error.message);
    console.log(error);

    process.exit(1);
}
};

module.exports = connectDB;
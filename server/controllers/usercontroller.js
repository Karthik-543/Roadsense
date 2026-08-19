const User = require("../models/User");
const bcrypt = require("bcrypt");

const registerUser = async (req, res) => {

    try {

        const { name, email, password, role } = req.body;

        if (!name || !email || !password || !role) {
            return res.status(400).json({
                message: "All fields are required"
            });
        }

        const existingUser = await User.findOne({ email });

        if (existingUser) {
            return res.status(409).json({
                message: "Email already exists"
            });
        }

        const hashedPassword = await bcrypt.hash(password, 10);

        await User.create({
            name,
            email,
            password: hashedPassword,
            role
        });

        return res.status(201).json({
            success: true,
            message: "User registered successfully"
        });

    } catch (error) {

        return res.status(500).json({
            message: "Internal Server Error"
        });

    }

};

module.exports = {
    registerUser
};
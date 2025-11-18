import bcrypt from "bcryptjs";
import jwt from "jsonwebtoken";
import User from "../models/user.model.js";
import RefreshToken from "../models/token.model.js";
import { v4 as uuidv4 } from "uuid";

export const register = async (req, res) => {
  try {
    const { username, email, password } = req.body;
    const hashed = await bcrypt.hash(password, 10);
    const user = await User.create({ username, email, password_hash: hashed });
    res.status(201).json({ message: "Usuario registrado", user });
  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const login = async (req, res) => {
  try {
    const { email, password } = req.body;
    const user = await User.findOne({ where: { email } });

    if (!user)
      return res.status(404).json({ message: "Usuario no encontrado" });

    const valid = await bcrypt.compare(password, user.password_hash);
    if (!valid)
      return res.status(401).json({ message: "Credenciales inválidas" });

    // ACCESS TOKEN (JWT)
    const token = jwt.sign(
      { id: user.id, role: user.role },
      process.env.JWT_SECRET,
      { expiresIn: "2h" }
    );

    // REFRESH TOKEN (UUID)
    const refreshToken = uuidv4();

    await RefreshToken.create({
      token: refreshToken,
      userId: user.id,
      expiresAt: new Date(Date.now() + 1000 * 60 * 60 * 24 * 7), // 7 días
    });

    res.json({
      message: "Login exitoso",
      accessToken: token,
      refreshToken: refreshToken,
    });

  } catch (error) {
    res.status(500).json({ error: error.message });
  }
};

export const refreshAccessToken = async (req, res) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken)
      return res.status(400).json({ message: "Refresh token requerido" });

    const stored = await RefreshToken.findByPk(refreshToken);

    if (!stored)
      return res.status(401).json({ message: "Refresh token inválido" });

    if (stored.expiresAt < new Date())
      return res.status(401).json({ message: "Refresh token expirado" });

    // Crear nuevo access token
    const newAccessToken = jwt.sign(
      { id: stored.userId },
      process.env.JWT_SECRET,
      { expiresIn: "15m" }
    );

    res.json({ accessToken: newAccessToken });

  } catch (error) {
    res.status(500).json({ message: "Error al refrescar token", error: error.message });
  }
};

export const verifyTokenController = async (req, res) => {
  const authHeader = req.headers.authorization;

  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    return res.status(401).json({ message: "Token no proporcionado o inválido" });
  }

  const token = authHeader.split(" ")[1];

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    // Opcional: puedes retornar también información básica del usuario
    res.status(200).json({
      valid: true,
      user: {
        id: decoded.id,
        role: decoded.role,
      },
    });
  } catch (error) {
    res.status(403).json({
      valid: false,
      message: "Token inválido o expirado",
      error: error.message,
    });
  }
};

export const logout = async (req, res) => {
  try {
    const { refreshToken } = req.body;

    if (!refreshToken)
      return res.status(400).json({ message: "Refresh token requerido" });

    await RefreshToken.destroy({ where: { token: refreshToken } });

    res.json({ message: "Sesión cerrada exitosamente" });

  } catch (error) {
    res.status(500).json({ message: "Error al cerrar sesión", error: error.message });
  }
};

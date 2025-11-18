import User from "../models/user.model.js";
import bcrypt from "bcryptjs";

// ============================
// GET /users/me
// ============================
export const getMyProfile = async (req, res) => {
  try {
    const user = await User.findByPk(req.user.id, {
      attributes: ["id", "username", "email", "role"],
    });

    res.json(user);
  } catch (error) {
    res.status(500).json({ message: "Error al obtener perfil", error: error.message });
  }
};

// ============================
// PUT /users/me
// ============================
export const updateMyProfile = async (req, res) => {
  try {
    const { username, email } = req.body;

    const user = await User.findByPk(req.user.id);
    if (!user) return res.status(404).json({ message: "Usuario no encontrado" });

    await user.update({ username, email });

    res.json({ message: "Perfil actualizado", user });
  } catch (error) {
    res.status(500).json({ message: "Error al actualizar perfil", error: error.message });
  }
};

// Crear usuario
export const createUser = async (req, res) => {
  try {
    const { username, email, password, role } = req.body;
    const password_hash = await bcrypt.hash(password, 10);
    const user = await User.create({ username, email, password_hash, role });
    res.status(201).json(user);
  } catch (error) {
    res.status(500).json({ message: "Error al crear usuario", error: error.message });
  }
};

// Obtener todos los usuarios
export const getUsers = async (req, res) => {
  try {
    const users = await User.findAll({
      attributes: ["id", "username", "email", "role", "createdAt", "updatedAt"],
    });
    res.json(users);
  } catch (error) {
    res.status(500).json({ message: "Error al obtener usuarios", error: error.message });
  }
};

// Obtener un usuario por ID
export const getUserById = async (req, res) => {
  try {
    const user = await User.findByPk(req.params.id, {
      attributes: ["id", "username", "email", "role", "createdAt", "updatedAt"],
    });
    if (!user) return res.status(404).json({ message: "Usuario no encontrado" });
    res.json(user);
  } catch (error) {
    res.status(500).json({ message: "Error al obtener usuario", error: error.message });
  }
};

// Actualizar usuario
export const updateUser = async (req, res) => {
  try {
    const { id } = req.params;
    const { username, email, role } = req.body;

    const user = await User.findByPk(id);
    if (!user) return res.status(404).json({ message: "Usuario no encontrado" });

    // Verificar permisos
    if (req.user.role !== "admin" && req.user.id !== id) {
      return res.status(403).json({ message: "No autorizado para actualizar este usuario" });
    }

    await user.update({ username, email, role });
    res.json({ message: "Usuario actualizado correctamente", user });
  } catch (error) {
    res.status(500).json({ message: "Error al actualizar usuario", error: error.message });
  }
};

// Eliminar usuario
export const deleteUser = async (req, res) => {
  try {
    const user = await User.findByPk(req.params.id);
    if (!user) return res.status(404).json({ message: "Usuario no encontrado" });

    await user.destroy();
    res.json({ message: "Usuario eliminado correctamente" });
  } catch (error) {
    res.status(500).json({ message: "Error al eliminar usuario", error: error.message });
  }
};

// ============================
// PUT /users/:id/role
// Solo Admin
// ============================
export const updateUserRole = async (req, res) => {
  try {
    const { id } = req.params;
    const { role } = req.body;

    const user = await User.findByPk(id);
    if (!user) return res.status(404).json({ message: "Usuario no encontrado" });

    await user.update({ role });

    res.json({ message: "Rol actualizado correctamente", user });
  } catch (error) {
    res.status(500).json({ message: "Error al actualizar rol", error: error.message });
  }
};
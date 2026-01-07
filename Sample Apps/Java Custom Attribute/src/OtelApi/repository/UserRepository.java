package OtelApi.repository;

import OtelApi.db.DatabaseUtil;
import OtelApi.model.User;

import java.sql.*;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;
import java.util.Optional;

public class UserRepository {

    public User create(User user) throws SQLException {
        String sql = "INSERT INTO users (username, email, full_name, age, salary, is_active, tags) VALUES (?, ?, ?, ?, ?, ?, ?)";

        try (Connection conn = DatabaseUtil.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, user.getUsername());
            stmt.setString(2, user.getEmail());
            stmt.setString(3, user.getFullName());
            stmt.setInt(4, user.getAge());
            stmt.setDouble(5, user.getSalary());
            stmt.setBoolean(6, user.isActive());
            stmt.setString(7, tagsToString(user.getTags()));

            stmt.executeUpdate();
            return user;
        }
    }

    public Optional<User> findByUsername(String username) throws SQLException {
        String sql = "SELECT username, email, full_name, age, salary, is_active, tags FROM users WHERE username = ?";

        try (Connection conn = DatabaseUtil.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, username);

            try (ResultSet rs = stmt.executeQuery()) {
                if (rs.next()) {
                    return Optional.of(mapRowToUser(rs));
                }
            }
        }
        return Optional.empty();
    }

    public List<User> findAll() throws SQLException {
        String sql = "SELECT username, email, full_name, age, salary, is_active, tags FROM users";
        List<User> users = new ArrayList<>();

        try (Connection conn = DatabaseUtil.getConnection();
             Statement stmt = conn.createStatement();
             ResultSet rs = stmt.executeQuery(sql)) {

            while (rs.next()) {
                users.add(mapRowToUser(rs));
            }
        }
        return users;
    }

    public User update(User user) throws SQLException {
        String sql = "UPDATE users SET email = ?, full_name = ?, age = ?, salary = ?, is_active = ?, tags = ? WHERE username = ?";

        try (Connection conn = DatabaseUtil.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, user.getEmail());
            stmt.setString(2, user.getFullName());
            stmt.setInt(3, user.getAge());
            stmt.setDouble(4, user.getSalary());
            stmt.setBoolean(5, user.isActive());
            stmt.setString(6, tagsToString(user.getTags()));
            stmt.setString(7, user.getUsername());

            int rowsAffected = stmt.executeUpdate();
            if (rowsAffected == 0) {
                throw new SQLException("User not found: " + user.getUsername());
            }
            return user;
        }
    }

    public boolean delete(String username) throws SQLException {
        String sql = "DELETE FROM users WHERE username = ?";

        try (Connection conn = DatabaseUtil.getConnection();
             PreparedStatement stmt = conn.prepareStatement(sql)) {

            stmt.setString(1, username);
            int rowsAffected = stmt.executeUpdate();
            return rowsAffected > 0;
        }
    }

    private User mapRowToUser(ResultSet rs) throws SQLException {
        return new User(
            rs.getString("username"),
            rs.getString("email"),
            rs.getString("full_name"),
            rs.getInt("age"),
            rs.getDouble("salary"),
            rs.getBoolean("is_active"),
            stringToTags(rs.getString("tags"))
        );
    }

    // Convert List<String> to comma-separated string for storage
    private String tagsToString(List<String> tags) {
        if (tags == null || tags.isEmpty()) {
            return "";
        }
        return String.join(",", tags);
    }

    // Convert comma-separated string back to List<String>
    private List<String> stringToTags(String tagsStr) {
        if (tagsStr == null || tagsStr.trim().isEmpty()) {
            return new ArrayList<>();
        }
        return new ArrayList<>(Arrays.asList(tagsStr.split(",")));
    }
}


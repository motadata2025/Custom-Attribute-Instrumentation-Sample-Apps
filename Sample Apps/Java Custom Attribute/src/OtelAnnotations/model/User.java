package OtelAnnotations.model;

import java.util.ArrayList;
import java.util.List;

public class User {
    private String username;      // String
    private String email;         // String
    private String fullName;      // String
    private int age;              // int
    private double salary;        // double (float)
    private boolean isActive;     // boolean
    private List<String> tags;    // List<String>

    public User() {
        this.tags = new ArrayList<>();
        this.isActive = true;
    }

    public User(String username, String email, String fullName, int age, double salary, boolean isActive, List<String> tags) {
        this.username = username;
        this.email = email;
        this.fullName = fullName;
        this.age = age;
        this.salary = salary;
        this.isActive = isActive;
        this.tags = tags != null ? tags : new ArrayList<>();
    }

    // Getters and Setters
    public String getUsername() {
        return username;
    }

    public void setUsername(String username) {
        this.username = username;
    }

    public String getEmail() {
        return email;
    }

    public void setEmail(String email) {
        this.email = email;
    }

    public String getFullName() {
        return fullName;
    }

    public void setFullName(String fullName) {
        this.fullName = fullName;
    }

    public int getAge() {
        return age;
    }

    public void setAge(int age) {
        this.age = age;
    }

    public double getSalary() {
        return salary;
    }

    public void setSalary(double salary) {
        this.salary = salary;
    }

    public boolean isActive() {
        return isActive;
    }

    public void setActive(boolean active) {
        isActive = active;
    }

    public List<String> getTags() {
        return tags;
    }

    public void setTags(List<String> tags) {
        this.tags = tags != null ? tags : new ArrayList<>();
    }

    @Override
    public String toString() {
        return "User{" +
                "username='" + username + '\'' +
                ", email='" + email + '\'' +
                ", fullName='" + fullName + '\'' +
                ", age=" + age +
                ", salary=" + salary +
                ", isActive=" + isActive +
                ", tags=" + tags +
                '}';
    }

    // Simple JSON serialization
    public String toJson() {
        StringBuilder tagsJson = new StringBuilder("[");
        if (tags != null && !tags.isEmpty()) {
            for (int i = 0; i < tags.size(); i++) {
                if (i > 0) tagsJson.append(",");
                tagsJson.append("\"").append(escapeJson(tags.get(i))).append("\"");
            }
        }
        tagsJson.append("]");

        return String.format(
            "{\"username\":\"%s\",\"email\":\"%s\",\"fullName\":\"%s\",\"age\":%d,\"salary\":%.2f,\"isActive\":%b,\"tags\":%s}",
            escapeJson(username), escapeJson(email), escapeJson(fullName), age, salary, isActive, tagsJson.toString()
        );
    }

    private String escapeJson(String value) {
        if (value == null) return "";
        return value.replace("\\", "\\\\")
                    .replace("\"", "\\\"")
                    .replace("\n", "\\n")
                    .replace("\r", "\\r")
                    .replace("\t", "\\t");
    }
}


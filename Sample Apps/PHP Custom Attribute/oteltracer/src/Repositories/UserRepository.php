<?php

namespace App\Repositories;

use App\Models\User;
use PDO;
use PDOException;

class UserRepository
{
    private PDO $db;
    private const TABLE_NAME = 'php_user_tbl';

    public function __construct(PDO $db)
    {
        $this->db = $db;
    }

    /**
     * Get all users with optional filters
     */
    public function findAll(array $filters = []): array
    {
        $query = "SELECT * FROM " . self::TABLE_NAME;
        $conditions = [];
        $params = [];

        if (isset($filters['is_active'])) {
            $conditions[] = "is_active = :is_active";
            $params[':is_active'] = $filters['is_active'];
        }

        if (!empty($conditions)) {
            $query .= " WHERE " . implode(' AND ', $conditions);
        }

        $query .= " ORDER BY id ASC";

        $stmt = $this->db->prepare($query);
        $stmt->execute($params);

        $users = [];
        while ($row = $stmt->fetch()) {
            // Convert PostgreSQL array to PHP array
            if (isset($row['tags']) && is_string($row['tags'])) {
                $row['tags'] = $this->parsePostgresArray($row['tags']);
            }
            $users[] = new User($row);
        }

        return $users;
    }

    /**
     * Find user by ID
     */
    public function findById(int $id): ?User
    {
        $query = "SELECT * FROM " . self::TABLE_NAME . " WHERE id = :id";
        $stmt = $this->db->prepare($query);
        $stmt->execute([':id' => $id]);

        $row = $stmt->fetch();
        if (!$row) {
            return null;
        }

        if (isset($row['tags']) && is_string($row['tags'])) {
            $row['tags'] = $this->parsePostgresArray($row['tags']);
        }

        return new User($row);
    }

    /**
     * Find user by username
     */
    public function findByUsername(string $username): ?User
    {
        $query = "SELECT * FROM " . self::TABLE_NAME . " WHERE username = :username";
        $stmt = $this->db->prepare($query);
        $stmt->execute([':username' => $username]);

        $row = $stmt->fetch();
        if (!$row) {
            return null;
        }

        if (isset($row['tags']) && is_string($row['tags'])) {
            $row['tags'] = $this->parsePostgresArray($row['tags']);
        }

        return new User($row);
    }

    /**
     * Create a new user
     */
    public function create(User $user): User
    {
        $query = "INSERT INTO " . self::TABLE_NAME . "
                  (username, email, full_name, age, salary, is_active, tags)
                  VALUES (:username, :email, :full_name, :age, :salary, :is_active, :tags)
                  RETURNING id, created_at, updated_at";

        $stmt = $this->db->prepare($query);
        $stmt->execute([
            ':username' => $user->getUsername(),
            ':email' => $user->getEmail(),
            ':full_name' => $user->getFullName(),
            ':age' => $user->getAge(),
            ':salary' => $user->getSalary(),
            ':is_active' => $user->isActive() ? 'true' : 'false',
            ':tags' => $this->arrayToPostgresArray($user->getTags()),
        ]);

        $result = $stmt->fetch();
        $user->setId($result['id']);
        $user->setCreatedAt($result['created_at']);
        $user->setUpdatedAt($result['updated_at']);

        return $user;
    }

    /**
     * Update an existing user
     */
    public function update(int $id, User $user): ?User
    {

        $query = "UPDATE " . self::TABLE_NAME . " 
                  SET username = :username, email = :email, full_name = :full_name, 
                      age = :age, salary = :salary, is_active = :is_active, tags = :tags
                  WHERE id = :id
                  RETURNING id, created_at, updated_at";

        $stmt = $this->db->prepare($query);
        $stmt->execute([
            ':id' => $id,
            ':username' => $user->getUsername(),
            ':email' => $user->getEmail(),
            ':full_name' => $user->getFullName(),
            ':age' => $user->getAge(),
            ':salary' => $user->getSalary(),
            ':is_active' => $user->isActive() ? 'true' : 'false',
            ':tags' => $this->arrayToPostgresArray($user->getTags()),
        ]);

        $result = $stmt->fetch();
        if (!$result) {
            return null;
        }

        $user->setId($result['id']);
        $user->setCreatedAt($result['created_at']);
        $user->setUpdatedAt($result['updated_at']);

        return $user;
    }

    /**
     * Delete a user
     */
    public function delete(int $id): bool
    {
        $query = "DELETE FROM " . self::TABLE_NAME . " WHERE id = :id";
        $stmt = $this->db->prepare($query);
        $result = $stmt->execute([':id' => $id]);

        return $result && $stmt->rowCount() > 0;
    }

    /**
     * Convert PHP array to PostgreSQL array format
     */
    private function arrayToPostgresArray(array $array): string
    {
        if (empty($array)) {
            return '{}';
        }
        return '{' . implode(',', array_map(function($item) {
            return '"' . str_replace('"', '\\"', $item) . '"';
        }, $array)) . '}';
    }

    /**
     * Parse PostgreSQL array to PHP array
     */
    private function parsePostgresArray(string $pgArray): array
    {
        if ($pgArray === '{}' || empty($pgArray)) {
            return [];
        }

        // Remove curly braces
        $pgArray = trim($pgArray, '{}');

        // Split by comma and clean up quotes
        $items = explode(',', $pgArray);
        return array_map(function($item) {
            return trim($item, '"');
        }, $items);
    }
}


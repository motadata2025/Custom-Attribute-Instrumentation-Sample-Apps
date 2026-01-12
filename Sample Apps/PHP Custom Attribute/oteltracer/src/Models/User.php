<?php

namespace App\Models;

use JsonSerializable;

class User implements JsonSerializable
{
    private ?int $id = null;
    private string $username;
    private string $email;
    private ?string $fullName = null;
    private ?int $age = null;
    private ?float $salary = null;
    private bool $isActive = true;
    private array $tags = [];
    private ?string $createdAt = null;
    private ?string $updatedAt = null;

    public function __construct(array $data = [])
    {
        if (!empty($data)) {
            $this->hydrate($data);
        }
    }

    public function hydrate(array $data): void
    {
        if (isset($data['id'])) {
            $this->id = (int) $data['id'];
        }
        if (isset($data['username'])) {
            $this->username = $data['username'];
        }
        if (isset($data['email'])) {
            $this->email = $data['email'];
        }
        if (isset($data['full_name'])) {
            $this->fullName = $data['full_name'];
        }
        if (isset($data['age'])) {
            $this->age = (int) $data['age'];
        }
        if (isset($data['salary'])) {
            $this->salary = (float) $data['salary'];
        }
        if (isset($data['is_active'])) {
            $this->isActive = (bool) $data['is_active'];
        }
        if (isset($data['tags'])) {
            $this->tags = is_array($data['tags']) ? $data['tags'] : json_decode($data['tags'], true) ?? [];
        }
        if (isset($data['created_at'])) {
            $this->createdAt = $data['created_at'];
        }
        if (isset($data['updated_at'])) {
            $this->updatedAt = $data['updated_at'];
        }
    }

    public function jsonSerialize(): array
    {
        return [
            'id' => $this->id,
            'username' => $this->username,
            'email' => $this->email,
            'full_name' => $this->fullName,
            'age' => $this->age,
            'salary' => $this->salary,
            'is_active' => $this->isActive,
            'tags' => $this->tags,
            'created_at' => $this->createdAt,
            'updated_at' => $this->updatedAt,
        ];
    }

    // Getters
    public function getId(): ?int { return $this->id; }
    public function getUsername(): string { return $this->username; }
    public function getEmail(): string { return $this->email; }
    public function getFullName(): ?string { return $this->fullName; }
    public function getAge(): ?int { return $this->age; }
    public function getSalary(): ?float { return $this->salary; }
    public function isActive(): bool { return $this->isActive; }
    public function getTags(): array { return $this->tags; }
    public function getCreatedAt(): ?string { return $this->createdAt; }
    public function getUpdatedAt(): ?string { return $this->updatedAt; }

    // Setters
    public function setId(?int $id): void { $this->id = $id; }
    public function setUsername(string $username): void { $this->username = $username; }
    public function setEmail(string $email): void { $this->email = $email; }
    public function setFullName(?string $fullName): void { $this->fullName = $fullName; }
    public function setAge(?int $age): void { $this->age = $age; }
    public function setSalary(?float $salary): void { $this->salary = $salary; }
    public function setIsActive(bool $isActive): void { $this->isActive = $isActive; }
    public function setTags(array $tags): void { $this->tags = $tags; }
    public function setCreatedAt(?string $createdAt): void { $this->createdAt = $createdAt; }
    public function setUpdatedAt(?string $updatedAt): void { $this->updatedAt = $updatedAt; }
}


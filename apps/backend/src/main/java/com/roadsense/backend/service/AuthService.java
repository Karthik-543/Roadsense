package com.roadsense.backend.service;

import com.roadsense.backend.dto.AuthDTO;
import com.roadsense.backend.exception.BadRequestException;
import com.roadsense.backend.exception.ResourceNotFoundException;
import com.roadsense.backend.model.User;
import com.roadsense.backend.repository.UserRepository;
import com.roadsense.backend.security.JwtTokenProvider;
import org.springframework.security.crypto.password.PasswordEncoder;
import org.springframework.stereotype.Service;

@Service
public class AuthService {

    private final UserRepository userRepository;
    private final PasswordEncoder passwordEncoder;
    private final JwtTokenProvider tokenProvider;

    public AuthService(UserRepository userRepository, PasswordEncoder passwordEncoder, JwtTokenProvider tokenProvider) {
        this.userRepository = userRepository;
        this.passwordEncoder = passwordEncoder;
        this.tokenProvider = tokenProvider;
    }

    public AuthDTO.AuthResponse register(AuthDTO.RegisterRequest request) {
        String cleanEmail = request.getEmail().trim().toLowerCase();

        if (userRepository.existsByEmail(cleanEmail)) {
            throw new BadRequestException("An account with this email address already exists.");
        }

        User user = User.builder()
                .email(cleanEmail)
                .password(passwordEncoder.encode(request.getPassword()))
                .fullName(request.getFullName().trim())
                .role("CITIZEN")
                .build();

        User saved = userRepository.save(user);

        String token = tokenProvider.generateToken(saved.getId(), saved.getEmail(), saved.getRole());

        return AuthDTO.AuthResponse.builder()
                .token(token)
                .tokenType("Bearer")
                .user(toUserDTO(saved))
                .build();
    }

    public AuthDTO.AuthResponse login(AuthDTO.LoginRequest request) {
        String cleanEmail = request.getEmail().trim().toLowerCase();

        User user = userRepository.findByEmail(cleanEmail)
                .orElseThrow(() -> new BadRequestException("Invalid email or password."));

        if (!passwordEncoder.matches(request.getPassword(), user.getPassword())) {
            throw new BadRequestException("Invalid email or password.");
        }

        String token = tokenProvider.generateToken(user.getId(), user.getEmail(), user.getRole());

        return AuthDTO.AuthResponse.builder()
                .token(token)
                .tokenType("Bearer")
                .user(toUserDTO(user))
                .build();
    }

    public AuthDTO.UserDTO getCurrentUser(String userId) {
        User user = userRepository.findById(userId)
                .orElseThrow(() -> new ResourceNotFoundException("User account not found."));
        return toUserDTO(user);
    }

    private AuthDTO.UserDTO toUserDTO(User user) {
        return AuthDTO.UserDTO.builder()
                .id(user.getId())
                .email(user.getEmail())
                .fullName(user.getFullName())
                .role(user.getRole())
                .createdAt(user.getCreatedAt() != null ? user.getCreatedAt().toString() : null)
                .build();
    }
}

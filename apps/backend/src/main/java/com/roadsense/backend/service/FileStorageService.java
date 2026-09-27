package com.roadsense.backend.service;

import com.roadsense.backend.exception.BadRequestException;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;
import java.nio.file.StandardCopyOption;
import java.util.UUID;

@Service
public class FileStorageService {

    private final Path uploadLocation;

    public FileStorageService(@Value("${storage.upload-dir:uploads/images}") String uploadDir) {
        this.uploadLocation = Paths.get(uploadDir).toAbsolutePath().normalize();
        try {
            Files.createDirectories(this.uploadLocation);
        } catch (IOException e) {
            throw new RuntimeException("Could not create image upload directory", e);
        }
    }

    public StoredFile storeFile(MultipartFile file) {
        if (file.isEmpty()) {
            throw new BadRequestException("Uploaded file is empty.");
        }

        String originalFilename = file.getOriginalFilename();
        String extension = "";
        if (originalFilename != null && originalFilename.contains(".")) {
            extension = originalFilename.substring(originalFilename.lastIndexOf("."));
        } else {
            extension = ".jpg";
        }

        String imageId = UUID.randomUUID().toString();
        String storedFilename = imageId + extension;
        Path targetPath = this.uploadLocation.resolve(storedFilename);

        try {
            Files.copy(file.getInputStream(), targetPath, StandardCopyOption.REPLACE_EXISTING);
        } catch (IOException e) {
            throw new RuntimeException("Failed to store file " + storedFilename, e);
        }

        return new StoredFile(imageId, originalFilename, targetPath.toString(), "/uploads/images/" + storedFilename);
    }

    public record StoredFile(String imageId, String originalFilename, String absolutePath, String relativeUrl) {}
}

# Stage 1: Build the application
FROM maven:3.9.6-eclipse-temurin-17 AS build
WORKDIR /app

# Step A: Copy ONLY the pom.xml
COPY pom.xml .

# Step B: Download all dependencies. 
# Docker will CACHE this step forever, unless you edit the pom.xml itself!
RUN mvn dependency:go-offline -B

# Step C: Copy the source code
COPY src ./src

# Step D: Compile the code (this runs instantly because dependencies are cached)
RUN mvn clean package -DskipTests

# Stage 2: Run the application (The runtime container)
FROM eclipse-temurin:17-jre-jammy
WORKDIR /app
COPY --from=build /app/target/api-0.0.1-SNAPSHOT.jar app.jar
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
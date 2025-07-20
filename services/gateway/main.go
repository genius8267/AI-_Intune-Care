package main

import (
	"log"
	"os"
	"time"

	"github.com/gofiber/fiber/v2"
	"github.com/gofiber/fiber/v2/middleware/cors"
	"github.com/gofiber/fiber/v2/middleware/logger"
	"github.com/gofiber/fiber/v2/middleware/recover"
	"github.com/gofiber/websocket/v2"
)

func main() {
	app := fiber.New(fiber.Config{
		ErrorHandler: customErrorHandler,
	})

	// Middleware
	app.Use(recover.New())
	app.Use(logger.New())
	app.Use(cors.New(cors.Config{
		AllowOrigins: os.Getenv("CORS_ORIGINS"),
		AllowHeaders: "Origin, Content-Type, Accept, Authorization",
	}))

	// Health check
	app.Get("/health", func(c *fiber.Ctx) error {
		return c.JSON(fiber.Map{
			"status": "healthy",
			"time":   time.Now().Unix(),
		})
	})

	// API routes
	api := app.Group("/api/v1")
	
	// Voice endpoint
	api.Post("/voice", handleVoiceInput)
	
	// WebSocket for real-time streaming
	app.Get("/ws", websocket.New(handleWebSocket))

	// Session management
	api.Post("/sessions", createSession)
	api.Get("/sessions/:id", getSession)
	api.Delete("/sessions/:id", endSession)

	// Metrics endpoint
	app.Get("/metrics", prometheusMetrics)

	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("Gateway starting on port %s", port)
	log.Fatal(app.Listen(":" + port))
}

func handleVoiceInput(c *fiber.Ctx) error {
	// Placeholder for voice processing
	return c.JSON(fiber.Map{
		"status": "processing",
		"message": "Voice input received",
	})
}

func handleWebSocket(c *websocket.Conn) {
	log.Println("WebSocket connection established")
	
	for {
		messageType, message, err := c.ReadMessage()
		if err != nil {
			log.Println("WebSocket read error:", err)
			break
		}
		
		// Echo for now (placeholder for real processing)
		if err := c.WriteMessage(messageType, message); err != nil {
			log.Println("WebSocket write error:", err)
			break
		}
	}
}

func createSession(c *fiber.Ctx) error {
	return c.JSON(fiber.Map{
		"session_id": "sess_" + generateID(),
		"created_at": time.Now().Unix(),
	})
}

func getSession(c *fiber.Ctx) error {
	sessionID := c.Params("id")
	return c.JSON(fiber.Map{
		"session_id": sessionID,
		"status": "active",
	})
}

func endSession(c *fiber.Ctx) error {
	sessionID := c.Params("id")
	return c.JSON(fiber.Map{
		"session_id": sessionID,
		"ended_at": time.Now().Unix(),
	})
}

func prometheusMetrics(c *fiber.Ctx) error {
	// Placeholder for Prometheus metrics
	return c.SendString(`# HELP http_requests_total Total HTTP requests
# TYPE http_requests_total counter
http_requests_total{method="GET",status="200"} 1027
`)
}

func customErrorHandler(c *fiber.Ctx, err error) error {
	code := fiber.StatusInternalServerError
	if e, ok := err.(*fiber.Error); ok {
		code = e.Code
	}
	
	return c.Status(code).JSON(fiber.Map{
		"error": err.Error(),
		"code": code,
	})
}

func generateID() string {
	// Simple ID generation (use UUID in production)
	return "abc123"
}
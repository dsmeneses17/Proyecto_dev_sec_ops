resource "google_compute_security_policy" "this" {
  name        = var.name
  description = var.description

  # Public owner registration accepts natural addresses like "Calle 1 # 11".
  # The SQLi preconfigured rule treats "#" in form data as a SQL comment, so
  # allow this public route before the WAF rules to avoid that false positive.
  rule {
    priority = 850
    action   = "allow"

    match {
      expr {
        expression = "request.path == '/registro'"
      }
    }

    description = "Allow owner registration form"
  }

  # OWASP: SQLi
  rule {
    priority = 1000
    action   = "deny(403)"

    match {
      expr {
        expression = "evaluatePreconfiguredWaf('sqli-v33-stable', {'sensitivity': 2})"
      }
    }

    description = "OWASP SQLi"
  }

  # OWASP: XSS
  rule {
    priority = 1010
    action   = "deny(403)"

    match {
      expr {
        expression = "evaluatePreconfiguredWaf('xss-v33-stable', {'sensitivity': 2})"
      }
    }

    description = "OWASP XSS"
  }

  # Rate limiting basico por IP
  rule {
    priority = 1100
    action   = "throttle"

    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }

    rate_limit_options {
      conform_action = "allow"
      exceed_action  = "deny(429)"

      rate_limit_threshold {
        count        = var.rate_limit_count
        interval_sec = var.rate_limit_interval_sec
      }

      enforce_on_key = "IP"
    }

    description = "Rate limit basico"
  }

  # Regla default
  rule {
    priority = 2147483647
    action   = "allow"

    match {
      versioned_expr = "SRC_IPS_V1"
      config {
        src_ip_ranges = ["*"]
      }
    }

    description = "Default allow"
  }
}

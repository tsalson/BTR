#!/bin/bash
# BDD → Robot Framework Pipeline Entry Point
# 
# This script serves as the entry point for the BTR pipeline.
# It handles environment setup and delegates to the Python orchestrator.
#
# Usage:
#   ./pipeline/run_pipeline.sh [OPTIONS] [FEATURE_FILES]
#   
# Examples:
#   ./pipeline/run_pipeline.sh bdd/features/login.feature
#   ./pipeline/run_pipeline.sh --all
#   ./pipeline/run_pipeline.sh --dry-run bdd/features/login.feature
#

set -euo pipefail

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
}

print_error() {
    echo -e "${RED}❌ ERROR: $1${NC}" >&2
}

print_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

# Check Python environment
check_python() {
    print_info "Checking Python environment..."
    
    # Check if Python is available
    if ! command -v python3 &> /dev/null; then
        print_error "Python3 not found. Please install Python 3.10 or higher."
        return 1
    fi
    
    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    print_info "Python version: $PYTHON_VERSION"
    
    # Check if uv is available (optional but recommended)
    if ! command -v uv &> /dev/null; then
        print_warning "uv package manager not found. Consider installing it for faster dependency management."
        print_warning "Install with: pip install uv"
    else
        print_success "uv found"
    fi
    
    return 0
}

# Check project structure
check_project_structure() {
    print_info "Checking project structure..."
    
    local required_dirs=(
        "bdd/features"
        "pipeline/prompts"
        "pipeline/schemas"
        "robot"
        ".kilo"
    )
    
    for dir in "${required_dirs[@]}"; do
        if [ ! -d "$PROJECT_ROOT/$dir" ]; then
            print_error "Missing directory: $dir"
            return 1
        fi
    done
    
    print_success "Project structure valid"
    return 0
}

# Check Python script
check_python_script() {
    print_info "Checking Python orchestrator script..."
    
    if [ ! -f "$SCRIPT_DIR/run_pipeline.py" ]; then
        print_error "Pipeline orchestrator script not found: $SCRIPT_DIR/run_pipeline.py"
        return 1
    fi
    
    print_success "Orchestrator script found"
    return 0
}

# Main execution
main() {
    # print_header "BTR Pipeline Orchestrator"
    
    # # Run pre-flight checks
    # print_header "Pre-flight Checks"
    # check_python || return 1
    # check_project_structure || return 1
    # check_python_script || return 1
    
    # print_success "All pre-flight checks passed"
    
    # # Run orchestrator
    print_header "Launching Pipeline"
    cd "$PROJECT_ROOT"
    python3 "$SCRIPT_DIR/run_pipeline.py" \
        --project-root "$PROJECT_ROOT" \
        "$@"
    
    return $?
}

# Trap errors
trap 'print_error "Pipeline failed"; exit 1' ERR

# Show help if requested
if [[ "${1:-}" == "--help" ]] || [[ "${1:-}" == "-h" ]]; then
    cat << 'EOF'
BTR Pipeline — BDD to Robot Framework Test Suite Generator

USAGE:
  ./pipeline/run_pipeline.sh [OPTIONS] [FEATURE_FILES]

OPTIONS:
  --all                 Process all .feature files in bdd/features/
  --from-file FILE      Load feature paths from a text file (one per line)
  --dry-run             Preview without executing agents
  --project-root PATH   Set project root directory (default: auto-detected)
  --help, -h            Show this help message

EXAMPLES:
  # Process a single feature file
  ./pipeline/run_pipeline.sh bdd/features/login.feature

  # Process multiple feature files
  ./pipeline/run_pipeline.sh bdd/features/login.feature bdd/features/checkout.feature

  # Process all features with dry-run
  ./pipeline/run_pipeline.sh --all --dry-run

  # Load features from a file
  ./pipeline/run_pipeline.sh --from-file feature_list.txt

OUTPUT:
  - bdd/ir/*.json                           — BDD Intermediate Representations
  - robot/suites/*.robot                    — Generated test suites
  - robot/resources/keywords/generated/     — Generated keyword resources
  - pipeline/run_summary.json               — Pipeline execution summary

For more information, see: pipeline/PIPELINE_GUIDE.md
EOF
    exit 0
fi

# Run main
main "$@"

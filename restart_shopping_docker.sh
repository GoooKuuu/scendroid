#!/bin/bash
# ============================================================
# Shopping Docker Quick restart script
# ============================================================
# Purpose: Restart the Shopping Docker container and reconfigure it
# 
# Usage scenarios:
#   - Docker After stopping or restarting
#   - Switch between different emulators
#   - Reconfigure base_url
#
# Not included: Compile/install APK (using setup_shopping_app.sh)
# ============================================================

# NOTE: Instead of using set -e, check each critical step manually

# ============================================================
# global variables
# ============================================================
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# ============================================================
# function
# ============================================================
print_info() {
    echo -e "${GREEN}$1${NC}"
}

print_warn() {
    echo -e "${YELLOW}$1${NC}"
}

print_error() {
    echo -e "${RED}$1${NC}"
}

calculate_port() {
    echo $((7770 + $1 - 5554))
}

fix_iptables() {
    print_info "🔧 Fix iptables..."
    sudo update-alternatives --set iptables /usr/sbin/iptables-nft
    sudo update-alternatives --set ip6tables /usr/sbin/ip6tables-nft
    sudo systemctl restart docker
    sleep 10
    print_info "✅ iptables Fixed"
}

# ============================================================
# Parse parameters
# ============================================================
EMULATOR_PORT=""
MODE=""  # Empty by default, select interactively later
AUTO_CONFIRM=false

while [[ $# -gt 0 ]]; do
    case $1 in
        -e|--emulator)
            EMULATOR_PORT="$2"
            shift 2
            ;;
        -m|--mode)
            MODE="$2"
            if [[ "$MODE" != "chrome" && "$MODE" != "app" ]]; then
                print_error "Invalid pattern: $MODE (Valid values: chrome, app)"
                exit 1
            fi
            shift 2
            ;;
        -y|--yes)
            AUTO_CONFIRM=true
            shift
            ;;
        -h|--help)
            echo "usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  -e, --emulator PORT   Emulator Port (such as 5554)"
            echo "  -m, --mode MODE       Run mode: chrome or app"
            echo "  -y, --yes             Skip confirmation"
            echo "  -h, --help            show help"
            echo ""
            echo "Example:"
            echo "  $0 -e 5554            # Interactive selection mode"
            echo "  $0 -e 5554 -m app -y  # App mode, automatic confirmation"
            echo "  $0 -e 5554 -m chrome  # Chrome model"
            exit 0
            ;;
        *)
            print_error "Unknown parameters: $1"
            exit 1
            ;;
    esac
done

# ============================================================
# Get parameters interactively
# ============================================================
if [ -z "$EMULATOR_PORT" ]; then
    print_info "Detect running emulator..."
    RUNNING=$(adb devices 2>/dev/null | grep emulator | awk '{print $1}' | sed 's/emulator-//')
    
    if [ -n "$RUNNING" ]; then
        echo "Find the running emulator:"
        for emu in $RUNNING; do
            echo "  • emulator-$emu"
        done
        echo ""
    fi
    
    read -p "Please enter the Emulator port number (e.g. 5554): " EMULATOR_PORT
fi

if ! [[ "$EMULATOR_PORT" =~ ^[0-9]+$ ]]; then
    print_error "Invalid port number: $EMULATOR_PORT"
    exit 1
fi

# Compute port and container name
SHOPPING_PORT=$(calculate_port $EMULATOR_PORT)
if [ "$EMULATOR_PORT" = "5554" ]; then
    CONTAINER_NAME="shopping"
else
    CONTAINER_NAME="shopping_${EMULATOR_PORT}"
fi

# Get host IP
HOST_IP=$(hostname -I | awk '{print $1}')
if [ -z "$HOST_IP" ]; then
    print_warn "Unable to get host IP, using default value"
    HOST_IP="127.0.0.1"
fi

# ============================================================
# If no mode is specified, select interactively
# ============================================================
if [ -z "$MODE" ]; then
    echo ""
    echo "======================================================"
    echo "🛒 Select Shopping access mode"
    echo "======================================================"
    echo ""
    echo "Please select access mode:"
    echo ""
    echo "  1) Chrome Browser mode (recommended for batch testing)"
    echo "     • Visit the Shopping website using Chrome browser"
    echo "     • Support CDP automatic login"
    echo "     • Suitable for batch automated testing"
    echo "     • No need to install APK"
    echo ""
    echo "  2) Shopping App Mode (recommended for presentations)"
    echo "     • Use native WebView App"
    echo "     • Better touch interaction experience"
    echo "     • Support WebView CDP automatic login"
    echo "     • Need to install APK first"
    echo ""
    read -p "Please select (1/2, default 1): " MODE_CHOICE
    
    case $MODE_CHOICE in
        2)
            MODE="app"
            print_info "✅ Selected: Shopping App mode"
            echo ""
            
            # Check if the app is installed
            if command -v adb &> /dev/null && [ -n "$(adb devices 2>/dev/null | grep emulator-${EMULATOR_PORT})" ]; then
                if ! adb -s emulator-${EMULATOR_PORT} shell pm list packages 2>/dev/null | grep -q "com.onestopshop.app"; then
                    print_warn "⚠️  Shopping App Not installed"
                    echo ""
                    echo "App mode requires the Shopping App to be installed first."
                    echo "Please run: ./setup_shopping_app.sh -e ${EMULATOR_PORT} -m app"
                    echo ""
                    read -p "Do you want to continue (manual installation later)? (yes/no): " CONTINUE
                    if [ "$CONTINUE" != "yes" ]; then
                        print_info "Operation canceled"
                        exit 0
                    fi
                fi
            fi
            ;;
        *)
            MODE="chrome"
            print_info "✅ Selected: Chrome browser mode"
            ;;
    esac
    echo ""
fi

# ============================================================
# Show configuration and confirm
# ============================================================
echo ""
echo "======================================================"
echo "🐳 Shopping Docker Restart configuration"
echo "======================================================"
echo ""
echo "  Emulator: emulator-${EMULATOR_PORT}"
echo "  Container name: ${CONTAINER_NAME}"
echo "  Port mapping: ${SHOPPING_PORT}:80"
echo "  Host IP: ${HOST_IP}"
echo "  Visit URL: http://${HOST_IP}:${SHOPPING_PORT}"
echo "  model: ${MODE}"
echo ""
echo "operate:"
echo "  1. Stop and delete the old container"
echo "  2. Create new container"
echo "  3. Configure Magento base_url"
echo "  4. Save mode configuration"
echo ""

if [ "$AUTO_CONFIRM" = false ]; then
    read -p "OK to continue? (yes/no): " CONFIRM
    if [ "$CONFIRM" != "yes" ]; then
        print_warn "Operation canceled"
        exit 0
    fi
fi

# ============================================================
# Step 1: Stop and delete the old container
# ============================================================
echo ""
print_info "📋 Step 1/4: Stop and delete the old container..."

docker stop $CONTAINER_NAME 2>/dev/null || print_warn "Container is not running"
docker rm $CONTAINER_NAME 2>/dev/null || print_warn "Container does not exist"

# ============================================================
# Step 2: Create new container
# ============================================================
echo ""
print_info "📋 Step 2/4: Create new container..."

if ! docker images | grep -q "shopping_final_0712"; then
    print_error "The mirror shopping_final_0712 does not exist!"
    echo ""
    echo "Please load the image first:"
    echo "  docker load --input shopping_final_0712.tar"
    exit 1
fi

print_info "Create container $CONTAINER_NAME (port: $SHOPPING_PORT)..."
echo "   Execute command: docker run --name $CONTAINER_NAME -p ${SHOPPING_PORT}:80 -d shopping_final_0712"

CREATE_OUTPUT=$(docker run --name $CONTAINER_NAME -p ${SHOPPING_PORT}:80 -d shopping_final_0712 2>&1)
CREATE_STATUS=$?

echo "   Command exit code: $CREATE_STATUS"

if [ $CREATE_STATUS -ne 0 ]; then
    echo ""
    print_error "Container creation failed!"
    echo ""
    echo "Error output:"
    echo "----------------------------------------"
    echo "$CREATE_OUTPUT"
    echo "----------------------------------------"
    echo ""
    
    # Check if it is an iptables problem
    if echo "$CREATE_OUTPUT" | grep -qi "iptables"; then
        print_warn "iptables related errors detected"
        echo ""
        read -p "Whether to try to repair iptables automatically? (yes/no): " FIX_CONFIRM
        
        if [ "$FIX_CONFIRM" = "yes" ]; then
            fix_iptables
            
            echo ""
            print_info "Try creating the container again..."
            CREATE_OUTPUT=$(docker run --name $CONTAINER_NAME -p ${SHOPPING_PORT}:80 -d shopping_final_0712 2>&1)
            CREATE_STATUS=$?
            
            if [ $CREATE_STATUS -ne 0 ]; then
                print_error "Still fails after repair"
                echo "$CREATE_OUTPUT"
                exit 1
            fi
            
            print_info "✅ Created successfully after repair"
        else
            echo ""
            print_error "Unable to continue, please fix it manually and try again"
            exit 1
        fi
    else
        # Other errors
        echo ""
        print_error "Container creation failed (non-iptables issue)"
        echo ""
        echo "Possible reasons:"
        echo "  1. port ${SHOPPING_PORT} Already occupied"
        echo "  2. Container name ${CONTAINER_NAME} Already exists"
        echo "  3. Docker Service exception"
        echo ""
        echo "Recommended action:"
        echo "  • Check port occupancy: netstat -tlnp | grep ${SHOPPING_PORT}"
        echo "  • Check the container: docker ps -a | grep ${CONTAINER_NAME}"
        echo "  • Manual removal: docker rm -f ${CONTAINER_NAME}"
        echo ""
        exit 1
    fi
else
    print_info "✅ Container created successfully"
    echo "   Container ID: $(echo $CREATE_OUTPUT | head -c 12)"
fi

# ============================================================
# Step 3: Configure Magento
# ============================================================
echo ""
print_info "📋 Step 3/4: Configure Magento..."

print_info "Waiting for the container to start..."
for i in {1..60}; do
    sleep 1
    echo -ne "\r⏳ $i/60 Second"
done
echo ""

if ! docker ps | grep -q $CONTAINER_NAME; then
    print_error "Container is not running!"
    exit 1
fi

print_info "update base_url..."
if docker exec $CONTAINER_NAME mysql -u magentouser -pMyPassword magentodb -e \
    "UPDATE core_config_data SET value='http://${HOST_IP}:${SHOPPING_PORT}/' WHERE path IN ('web/unsecure/base_url','web/secure/base_url');" 2>/dev/null; then
    echo "   ✓ base_url Update successful"
else
    print_warn "base_url Update failed (possibly MySQL is not ready)"
fi

print_info "Disable HTTPS..."
docker exec $CONTAINER_NAME mysql -u magentouser -pMyPassword magentodb -e \
    "UPDATE core_config_data SET value='0' WHERE path IN ('web/secure/use_in_frontend','web/secure/use_in_adminhtml');" >/dev/null 2>&1
echo "   ✓ HTTPS Disabled"

print_info "Remove cookie restrictions..."
docker exec $CONTAINER_NAME mysql -u magentouser -pMyPassword magentodb -e \
    "DELETE FROM core_config_data WHERE path='web/cookie/cookie_domain';" >/dev/null 2>&1
echo "   ✓ Cookie Restriction removed"

print_info "Refresh cache..."
docker exec $CONTAINER_NAME /var/www/magento2/bin/magento cache:flush >/dev/null 2>&1
echo "   ✓ cache flushed"

print_info "Restart web service..."
docker exec $CONTAINER_NAME supervisorctl restart nginx php-fpm >/dev/null 2>&1 || true
echo "   ✓ Web Service has been restarted"

print_info "✅ Magento Configuration completed"

# ============================================================
# Step 4: Verify and save configuration
# ============================================================
echo ""
print_info "📋 Step 4/4: Verify and save configuration..."

# Verify website
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://${HOST_IP}:${SHOPPING_PORT} 2>/dev/null || echo "")
if [ "$HTTP_CODE" = "200" ] || [ "$HTTP_CODE" = "301" ] || [ "$HTTP_CODE" = "302" ]; then
    print_info "✅ Website accessible (HTTP $HTTP_CODE)"
else
    print_warn "Website response: HTTP $HTTP_CODE (may be normal)"
fi

# Save mode configuration
MODE_CONFIG="/tmp/shopping_mode.conf"
cat > "$MODE_CONFIG" << EOF
# Shopping mode configuration
# Generated: $(date)
SHOPPING_MODE=${MODE}
EMULATOR_PORT=${EMULATOR_PORT}
SHOPPING_PORT=${SHOPPING_PORT}
HOST_IP=${HOST_IP}
SHOPPING_URL=http://${HOST_IP}:${SHOPPING_PORT}
EOF

# Save environment variables
ENV_FILE="/tmp/shopping_env_${EMULATOR_PORT}.sh"
cat > "$ENV_FILE" << EOF
# Shopping environment variables
export SHOPPING='http://${HOST_IP}:${SHOPPING_PORT}'
export SHOPPING_ADMIN='http://${HOST_IP}:${SHOPPING_PORT}/admin'
EOF

print_info "✅ Configuration saved"

# ============================================================
# Finish
# ============================================================
echo ""
echo "======================================================"
print_info "✅ Docker Restart complete!"
echo "======================================================"
echo ""
echo "📊 System status:"
echo "  • container: ${CONTAINER_NAME} (running)"
echo "  • port: ${SHOPPING_PORT}"
echo "  • URL: http://${HOST_IP}:${SHOPPING_PORT}"
echo "  • model: ${MODE}"
echo ""
echo "📝 Configuration file:"
echo "  • ${MODE_CONFIG}"
echo "  • ${ENV_FILE}"
echo ""
echo "🎯 Start testing:"
if [ "$MODE" = "app" ]; then
    echo "  1. Make sure the Shopping App is installed"
    echo "  2. Run: python run_layered_tui_test.py"
else
    echo "  1. Run: python run_layered_tui_test.py"
fi
echo ""

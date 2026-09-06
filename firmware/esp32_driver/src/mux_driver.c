#include "mux_driver.h"
#include "config.h"
#include <stdio.h>

#ifdef ESP_PLATFORM
#include "driver/gpio.h"
#include "esp_rom_sys.h"
#define DELAY_US(us) esp_rom_delay_us(us)
#else
#include <unistd.h>
#define DELAY_US(us) usleep(us)
#endif

static uint8_t s_current_channel = 0;
static bool s_enabled = false;

void mux_init(void) {
#ifdef ESP_PLATFORM
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << PIN_MUX_S0) |
                        (1ULL << PIN_MUX_S1) |
                        (1ULL << PIN_MUX_S2) |
                        (1ULL << PIN_MUX_S3) |
                        (1ULL << PIN_MUX_EN),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_ENABLE,
        .intr_type = GPIO_INTR_DISABLE,
    };
    gpio_config(&io_conf);
#endif
    mux_disable();
    mux_select_channel(0);
}

void mux_select_channel(uint8_t channel) {
    if (channel >= GRID_TOTAL_CELLS) {
        channel = GRID_TOTAL_CELLS - 1;
    }
    s_current_channel = channel;

#ifdef ESP_PLATFORM
    uint8_t s0 = (channel >> 0) & 0x01;
    uint8_t s1 = (channel >> 1) & 0x01;
    uint8_t s2 = (channel >> 2) & 0x01;
    uint8_t s3 = (channel >> 3) & 0x01;

    gpio_set_level(PIN_MUX_S0, s0);
    gpio_set_level(PIN_MUX_S1, s1);
    gpio_set_level(PIN_MUX_S2, s2);
    gpio_set_level(PIN_MUX_S3, s3);
#endif

    /* Allow analog switch and tank circuit to settle */
    DELAY_US(MUX_SETTLE_US);
}

void mux_enable(void) {
    s_enabled = true;
#ifdef ESP_PLATFORM
    /* Active-Low EN: 0 = Enabled */
    gpio_set_level(PIN_MUX_EN, 0);
#endif
}

void mux_disable(void) {
    s_enabled = false;
#ifdef ESP_PLATFORM
    /* Active-Low EN: 1 = Disabled / High-Z */
    gpio_set_level(PIN_MUX_EN, 1);
#endif
}

uint8_t mux_get_current_channel(void) {
    return s_current_channel;
}

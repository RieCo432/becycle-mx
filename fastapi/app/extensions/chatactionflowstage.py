from enum import Enum


class ChatActionFlowStage(Enum):
    BOOKING_ELICITING = "booking_eliciting"
    BOOKING_AWAITING_SLOT_CHOICE = "booking_awaiting_slot_choice"
    BOOKING_AWAITING_CONFIRM = "booking_awaiting_confirm"

from enum import Enum


class ChatActionFlowStage(Enum):
    BOOKING_ELICITING = "booking_eliciting"
    BOOKING_AWAITING_SLOT_CHOICE = "booking_awaiting_slot_choice"

export const rangeValidator = (value, start, end) => {
    if (value >= start && value <= end) {
        return true;
    }

    return false;
};
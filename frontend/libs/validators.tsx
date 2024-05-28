export const rangeValidator = (value, start, end) => {
    if (value < start || value > end) {
        return false;
    }

    return true;
};
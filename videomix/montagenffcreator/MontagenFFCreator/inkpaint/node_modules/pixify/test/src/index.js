module.exports = function(){
    var result;

    // @if DEBUG
    result = true;
    // @endif

    // @if RELEASE
    result = false;
    // @endif
    
    return result;
};